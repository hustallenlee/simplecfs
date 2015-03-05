# -*- coding: utf-8 -*-
"""
mds network server and the main controller
"""
import eventlet
import logging

from simplecfs.mds.meta_storage import MDSStore
from simplecfs.message.network_handler import recv_command  # , send_command


class MDSServer(object):
    """mds server to handle network request and response"""

    def __init__(self, config):
        """@config: ConfigParser() object"""
        self._config = config

        mds_ip = config.get('mds', 'mds_ip')
        mds_port = config.getint('mds', 'mds_port')
        self._server = eventlet.listen((mds_ip, mds_port))

        thread_num = config.getint('threads', 'thread_num')
        self._pool = eventlet.GreenPool(thread_num)

        redis_host = config.get('redis', 'host')
        redis_port = config.getint('redis', 'port')
        redis_db = config.getint('redis', 'db')
        logging.info('set redis host:ip db: %s:%d %d', redis_host,
                     redis_port, redis_db)
        self.mds = MDSStore(host=redis_host, port=redis_port, db=redis_db)

        self._handlers = {
            # OP_ADD_CHUNK: self._handle_add_chunk,
        }

#     def _handle_add_chunk(self, filed, args):
#         """handle client -> ds add chunk request, and response"""
#         logging.info('handle add chunk request')
#
#         # receive data from client
#         chunk_id = args['chunk_id']
#         data = recv_data(filed)
#
#         # write data to local filesystem
#         state = self._ds.write_chunk(chunk_id, data)
#         logging.info('add chunk: %s', chunk_id)
#
#         # reply to client
#         reply = AddChunkReplyPacket(state)
#         msg = reply.get_message()
#         logging.info("add chunk return: %s", msg)
#         send_command(filed, msg)

    def _handle_conncetion(self, filed):
        """handle connected socket as a file"""
        logging.info('connection start')

        command = recv_command(filed)
        self._handlers[command['method']](filed, command)

        filed.close()
        logging.info('disconnected')

    def start(self):
        """
        start mds server
        """
        while True:
            try:
                sock, address = self._server.accept()
                logging.info('accepted %s:%s', address[0], address[1])
                self._pool.spawn_n(self._handle_conncetion, sock.makefile('rw'))
            except (SystemExit, KeyboardInterrupt):
                break
