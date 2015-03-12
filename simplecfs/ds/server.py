# -*- coding: utf-8 -*-
"""
dateserver network server
"""
import sys
import eventlet
import logging
import socket

from simplecfs.ds.local_storage import DSStore
from simplecfs.message.packet import AddChunkReplyPacket,\
    DeleteChunkReplyPacket, GetChunkReplyPacket, AddDSPacket
from simplecfs.common.parameters import OP_ADD_CHUNK, OP_DELETE_CHUNK,\
    OP_GET_CHUNK, RET_FAILURE
from simplecfs.message.network_handler import recv_command,\
    recv_data, send_command, send_data


class DSServer(object):
    """data server to handle network request and response"""

    def __init__(self, config, test=False):
        """@config: ConfigParser() object"""
        self._config = config

        ds_ip = config.get('dataserver', 'ds_ip')
        ds_port = config.getint('dataserver', 'ds_port')
        self._server = eventlet.listen((ds_ip, ds_port))

        thread_num = config.getint('threads', 'thread_num')
        self._pool = eventlet.GreenPool(thread_num)

        store_dir = config.get('storage', 'chunk_store_dir')
        logging.info('get store dir: %s', store_dir)
        self._ds = DSStore(store_dir)

        # register to mds when not in testmode
        if not test:
            mds_ip = config.get('mds', 'mds_ip')
            mds_port = config.getint('mds', 'mds_port')
            self._add_ds(mds_ip, mds_port)

        # handler for request to ds
        self._handlers = {
            OP_ADD_CHUNK: self._handle_add_chunk,
            OP_DELETE_CHUNK: self._handle_delete_chunk,
            OP_GET_CHUNK: self._handle_get_chunk,
        }

    def _add_ds(self, mds_ip='127.0.0.1', mds_port=8000):
        """register ds to mds"""
        logging.info('add ds to mds')
        rack_id = self._config.getint('dataserver', 'rack_id')
        ds_ip = self._config.get('dataserver', 'ds_ip')
        ds_port = self._config.getint('dataserver', 'ds_port')

        packet = AddDSPacket(rack_id, ds_ip, ds_port)
        msg = packet.get_message()

        try:
            sock = eventlet.connect((mds_ip, mds_port))
        except socket.error:
            logging.error('can not connect to mds %s:%d', mds_ip, mds_port)
            sys.exit('can not connect to mds, start mds and set the conf file!')
        sock_fd = sock.makefile('rw')

        logging.info('add ds msg: %s', msg)
        send_command(sock_fd, msg)

        recv = recv_command(sock_fd)
        state = recv['state']
        if state == RET_FAILURE:
            logging.error('add ds error, return :%s', recv)
            sys.exit('add ds error, mds return ' + recv)

        sock_fd.close()
        return state

    def _handle_add_chunk(self, filed, args):
        """handle client -> ds add chunk request, and response"""
        logging.info('handle add chunk request')

        # receive data from client
        chunk_id = args['chunk_id']
        data = recv_data(filed)

        # write data to local filesystem
        state = self._ds.write_chunk(chunk_id, data)
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
        state = self._ds.remove_chunk(chunk_id)
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
        state, data = self._ds.read_chunk(chunk_id, total, lists)
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
