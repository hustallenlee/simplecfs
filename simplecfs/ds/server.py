# -*- coding: utf-8 -*-
"""
dateserver network server
"""
import eventlet
import logging


class DSServer(object):
    """data server to handle network request and response"""

    def __init__(self, config):
        """@config: ConfigParser() object"""
        self._config = config

        ds_ip = config.get('dataserver', 'ds_ip')
        ds_port = config.getint('dataserver', 'ds_port')
        self._server = eventlet.listen((ds_ip, ds_port))

        thread_num = config.getint('threads', 'thread_num')
        self._pool = eventlet.GreenPool(thread_num)

    def _handle_conncetion(self, filed):
        """handle connected socket as a file"""
        logging.info('connection handler')
        while True:
            # pass through every non-eof line
            line = filed.readline()
            logging.info('recv: %s', line)
            if not line:
                break
            filed.write(line)
            filed.flush()
        logging.info('client disconnected')

    def start(self):
        """
        start data server
        """
        while True:
            try:
                sock, address = self._server.accept()
                logging.info('accepted %s:%s', address[0], address[1])
                self._pool.spawn_n(self._handle_conncetion, sock.makefile('rw'))
            except (SystemExit, KeyboardInterrupt):
                break
