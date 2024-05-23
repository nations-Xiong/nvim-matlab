#!/usr/bin/env python3

import pexpect
import socketserver
import sys
import os
import signal
import time
import random
import string
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rplugin/python3'))
from nvim_matlab.logger import logger


MAX_LENGTH = 64
MAX_RETRY = 3
VAR_LENGTH = 12


def start_thread(target=None, args=()):
    t = threading.Thread(target=target, args=args)
    t.daemon = True
    t.start()


def forward_input(matlab):
    """Forward stdin to Matlab.proc's stdin."""
    matlab.proc.interact()


auto_restart = False
def status_monitor_thread(matlab):
    while True:
        matlab.proc.wait()
        if not auto_restart:
            break
        logger.debug('Restarting')
        matlab.launch()
        start_thread(target=forward_input, args=(matlab,))
        time.sleep(1)

    global server
    logger.info('Shutting down server')
    server.shutdown()
    server.server_close()
    logger.info(f"Connection closed: {server.client_address}")


class Matlab():
    def __init__(self):
        self.launch()

    def launch(self):
        self.kill()
        self.proc = pexpect.spawn('matlab', ['-nosplash', '-nodesktop'])
        return self.proc

    def kill(self):
        try:
            os.killpg(self.proc.pid, signal.SIGTERM)
        except:
            pass

    def cancel(self):
        os.kill(self.proc.pid, signal.SIGINT)

    def exec(self, code, timer=False):
        num_retry = 0
        
        if timer:
            rand_var = ''.join([random.choice(string.ascii_uppercase) for _ in range(VAR_LENGTH)])
            cmd = (f"{randvar}=tic; {code}, try, toc({randvar}), catch, end, clear('{randvar}');\n")
        else:
            cmd = f"{code.strip()}\n"

        # The maximum number of characters allowed on a single line in Matlab's CLI is 4096.
        delim = ' ...\n'
        line_size = 4095 - len(delim)
        cmd = delim.join([cmd[i:i+line_size] for i in range(0, len(cmd), line_size)])

        while num_retry < MAX_RETRY:
            try:
                global HIDE_UNTIL_NEWLINE
                HIDE_UNTIL_NEWLINE = True
                self.proc.send(cmd)
                break
            except Exception as ex:
                logger.error(f"{ex}")
                num_retry += 1
                self.launch()
                time.sleep(1)


class TCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        logger.info(f"New connection: {self.client_address}")
        while True:
            msg = self.rfile.readline()
            if not msg:
                break
            msg = msg.decode('utf-8').strip()

            logger.debug(f"{msg=}")

            options = {
                'kill': self.server.matlab.kill,
                'cancel': self.server.matlab.cancel,
            }

            if msg in options:
                options[msg]()
            else:
                self.server.matlab.exec(msg)



if __name__=='__main__':
    logger.info('Starting Matlab server')

    host, port = 'localhost', 65535
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), TCPHandler)
    server.matlab = Matlab()

    start_thread(target=forward_input, args=(server.matlab,))
    start_thread(target=status_monitor_thread, args=(server.matlab,))

    logger.info('Matlab server started')
    server.serve_forever()
