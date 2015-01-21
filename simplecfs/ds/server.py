# -*- coding: utf-8 -*-
"""
dateserver network server
"""
import eventlet
import logging

from simplecfs.ds.local_storage import DSStore
from simplecfs.message.packet import AddChunkReplyPacket
from simplecfs.common.parameters import RET_SUCCESS
from simplecfs.common.network_handler import recv_command,\
    recv_data, send_command


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
        self._handlers = {
            'ADD_CHUNK': self._handle_add_chunk,
        }

    def _handle_add_chunk(self, filed, args):
        """handle client -> ds add chunk request, and response"""
        logging.info('handle add chunk request')

        # receive data from client
        chunk_id = args['chunk_id']
        data = recv_data(filed)

        # write data to local filesystem
        store_dir = self._config.get('storage', 'chunk_store_dir')
        logging.info('get store dir: %s', store_dir)
        ds_ = DSStore(store_dir)
        ds_.write_chunk(chunk_id, data)
        logging.info('add chunk: %s', chunk_id)

        # reply to client
        reply = AddChunkReplyPacket(state=RET_SUCCESS)
        msg = reply.get_message()
        logging.info("add chunk return: %s", msg)
        send_command(filed, msg)

    def _handle_conncetion(self, filed):
        """handle connected socket as a file"""
        logging.info('connection start')

        command = recv_command(filed)
        self._handlers[command['method']](filed, command)

        filed.close()
        logging.info('disconnected')

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
