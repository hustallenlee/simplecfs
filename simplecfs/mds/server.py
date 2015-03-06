# -*- coding: utf-8 -*-
"""
mds network server and the main controller
"""
import eventlet
import logging
import time

from simplecfs.mds.meta_storage import MDSStore
from simplecfs.message.network_handler import recv_command, send_command
from simplecfs.common.parameters import RET_SUCCESS, RET_FAILURE, OP_MAKE_DIR
from simplecfs.message.packet import MakeDirReplyPacket


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
            OP_MAKE_DIR: self._handle_make_dir,
        }

    def _isvalid_dirname(self, dirname):
        ret = RET_SUCCESS
        info = 'ok'

        if not dirname:  # empty
            ret = RET_FAILURE
            info = 'empty dirname'

        if dirname == '/':
            ret = RET_FAILURE
            info = 'dir name is root'

        if not dirname.startswith('/'):
            ret = RET_FAILURE
            info = 'dirname should be abusolute path'

        if not dirname.endswith('/'):
            ret = RET_FAILURE
            info = 'dirname should end with /'

        return (ret, info)

    def _handle_make_dir(self, filed, args):
        """handle client -> mds make dir request, and response"""
        logging.info('handle make dir request')

        # get the dirname
        dirname = args['dirname']

        state = RET_SUCCESS
        info = ''

        # check dirname valid
        state, info = self._isvalid_dirname(dirname)

        # check parent exists
        if state == RET_SUCCESS:
            parent = ''.join(dirname[:-1].rpartition('/')[0:2])
            if not self.mds.hasdir(parent):
                state = RET_FAILURE
                info = 'mkdir parent no exists: ' + parent

        # check dir exists
        if state == RET_SUCCESS:
            if self.mds.hasdir(dirname):
                state = RET_FAILURE
                info = 'directory already exists: ' + dirname

        # write to meta db
        if state == RET_SUCCESS:
            dirinfo = {}
            dirinfo['parent_dir'] = parent
            dirinfo['create_time'] = time.asctime()

            state = self.mds.mkdir(dirname, dirinfo)
            if state == RET_FAILURE:
                info = 'mds mkdir error'

        # reply to client
        reply = MakeDirReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("make dir return: %s", msg)
        send_command(filed, msg)

    def _handle_conncetion(self, filed):
        """handle connected socket as a file"""
        logging.info('connection start')

        command = recv_command(filed)
        try:
            self._handlers[command['method']](filed, command)
        except KeyError:
            logging.exception("no such command handler: %s", command)

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
