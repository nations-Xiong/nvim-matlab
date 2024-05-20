#!/usr/bin/env python

import logging


def logger_init():
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='/tmp/matlab_server.log',
                        encoding='utf-8',
                        level=logging.DEBUG,  # DEBUG is lower than INFO
                        format='%(asctime)s [%(levelname)s]: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    return logger


logger = logger_init()
