#!/usr/bin/env python

import socket
from threading import Timer
import time

from .logger import logger

TIME_DELAY_ADD_PATH = 5
MAX_RETRY = 3
RETRY_INTERVAL = 2


class MatlabCliController():
    def __init__(self):
        self.host = 'localhost'
        self.port = 65535
        self.connect_to_server()

    def connect_to_server(self):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.connect('/tmp/matlab-server.sock')
        Timer(TIME_DELAY_ADD_PATH, self.setup_path).start()

    def disconnect_to_server(self):
        self.s.close()

    def exec_code(self, code_lines):
        code = '\n'.join(code_lines)
        code += '\n'

        num_retry = 0
        while num_retry < MAX_RETRY:
            try:
                logger.info(f"{code=}")
                self.s.sendall(code.encode('utf-8'))
            except Exception as ex:
                logger.error(f"{ex}")
                self.connect_to_server()
                num_retry += 1
                time.sleep(RETRY_INTERVAL)
            else:
                # no exception happens
                break

    def doc_command(self, command):
        self.exec_code([f"doc {command};"])

    def help_name(self, name):
        self.exec_code([f"help {name};"])

    def setup_path(self):
        pass

    def send_ctrl_c(self):
        self.s.sendall('cancel\n'.encode('utf-8'))

    def send_kill(self):
        self.s.sendall('kill\n'.encode('utf-8'))
