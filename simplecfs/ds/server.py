# -*- coding: utf-8 -*-
"""
dateserver network server
"""
import eventlet
import logging

from simplecfs.ds.local_storage import DSStore
from simplecfs.message.packet import AddChunkReplyPacket,\
    DeleteChunkReplyPacket, GetChunkReplyPacket
from simplecfs.common.parameters import OP_ADD_CHUNK, OP_DELETE_CHUNK,\
    OP_GET_CHUNK
from simplecfs.message.network_handler import recv_command,\
    recv_data, send_command, send_data


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
            OP_ADD_CHUNK: self._handle_add_chunk,
            OP_DELETE_CHUNK: self._handle_delete_chunk,
            OP_GET_CHUNK: self._handle_get_chunk,
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
        state = ds_.write_chunk(chunk_id, data)
        logging.info('add chunk: %s', chunk_id)

        # reply to client
        reply = AddChunkReplyPacket(state)
        msg = reply.get_message()
        logging.info("add chunk return: %s", msg)
        send_command(filed, msg)

    def _handle_delete_chunk(self, filed, args):
        """handle client -> ds delete chunk request, and response"""
        logging.info('handle delete chunk request')

        chunk_id = args['chunk_id']

        # delete local filesystem chunk
        store_dir = self._config.get('storage', 'chunk_store_dir')
        logging.info('get store dir: %s', store_dir)
        ds_ = DSStore(store_dir)
        state = ds_.remove_chunk(chunk_id)
        logging.info('add chunk: %s', chunk_id)

        # reply to client
        reply = DeleteChunkReplyPacket(state)
        msg = reply.get_message()
        logging.info("delete chunk return: %s", msg)
        send_command(filed, msg)

    def _handle_get_chunk(self, filed, args):
        """handle client -> ds get chunk requst, and response"""
        logging.info('handle get chunk request')

        chunk_id = args['chunk_id']
        total = args['total']
        lists = args['list']
        logging.info('get chunk: %s', chunk_id)

        # get data from local filesystem
        store_dir = self._config.get('storage', 'chunk_store_dir')
        logging.info('get store dir: %s', store_dir)
        ds_ = DSStore(store_dir)
        state, data = ds_.read_chunk(chunk_id, total, lists)
        logging.info('read chunk return: %d', state)

        # reply state
        reply = GetChunkReplyPacket(state)
        msg = reply.get_message()
        logging.info("get chunk return: %s", msg)
        send_command(filed, msg)

        # reply data
        if isinstance(data, list):
            data = b''.join(data)
        send_data(filed, data)

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
