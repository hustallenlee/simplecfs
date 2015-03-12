# -*- coding: utf-8 -*-
"""
mds network server and the main controller
"""
import eventlet
import logging
import time
import socket

from simplecfs.mds.meta_storage import MDSStore
from simplecfs.message.network_handler import recv_command, send_command
from simplecfs.common.parameters import RET_SUCCESS, RET_FAILURE, OP_MAKE_DIR,\
    OP_REMOVE_DIR, OP_LIST_DIR, OP_STATUS_DIR, OP_VALID_DIR, OP_ADD_DS,\
    OP_REPORT_DS, DS_CONNECTED, DS_BROKEN
from simplecfs.message.packet import MakeDirReplyPacket, RemoveDirReplyPacket,\
    ListDirReplyPacket, StatusDirReplyPacket, ValidDirReplyPacket,\
    AddDSReplyPacket, ReportDSReplyPacket


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
            OP_ADD_DS: self._handle_add_ds,
            OP_REPORT_DS: self._handle_report_ds,
            OP_MAKE_DIR: self._handle_make_dir,
            OP_REMOVE_DIR: self._handle_remove_dir,
            OP_LIST_DIR: self._handle_list_dir,
            OP_STATUS_DIR: self._handle_status_dir,
            OP_VALID_DIR: self._handle_valid_dir,
        }

    def _check_ds(self, ds_ip, ds_port):
        """check ds status and change the meta data"""

        state = DS_CONNECTED
        try:
            eventlet.connect((ds_ip, ds_port))
        except socket.error:
            logging.exception('can not connet to ds')
            state = DS_BROKEN

        # update ds state
        value = self.mds.getds(ds_ip, ds_port)
        value['status'] = state
        ret = self.mds.updateds(ds_ip, ds_port, value)

        return ret

    def _handle_add_ds(self, filed, args):
        """handle ds -> mds add ds request, and response"""
        logging.info('handle add ds request')

        # get the ds info
        rack_id = args['rack_id']
        ds_ip = args['ds_ip']
        ds_port = args['ds_port']
        ds_info = {
            'ip': ds_ip,
            'port': ds_port,
            'rack': rack_id,
            'status': DS_CONNECTED,
            'update_time': time.asctime(),
        }

        state = RET_SUCCESS
        info = 'ok'

        # write to meta db
        state = self.mds.addds(ds_ip, ds_port, ds_info)
        if state == RET_FAILURE:
            info = 'mds addds error'

        # reply to client
        reply = AddDSReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("add ds return: %s", msg)
        send_command(filed, msg)

    def _handle_report_ds(self, filed, args):
        """handle ds -> mds report ds request, and response"""
        logging.info('handle report ds request')

        # get the ds info
        ds_ip = args['ds_ip']
        ds_port = args['ds_port']
        ds_info = args['info']

        state = RET_SUCCESS
        info = 'ok'

        # write to meta db
        value = self.mds.getds(ds_ip, ds_port)
        for key in ds_info.keys():
            value[key] = ds_info[key]

        value['update_time'] = time.asctime()
        state = self.mds.updateds(ds_ip, ds_port, value)
        if state == RET_FAILURE:
            info = 'report ds error'

        # reply to client
        reply = ReportDSReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("report ds return: %s", msg)
        send_command(filed, msg)

    def _isvalid_dirname(self, dirname):
        """check weather dirname is a valid path name"""
        ret = RET_SUCCESS
        info = 'ok'

        if not dirname:  # empty
            ret = RET_FAILURE
            info = 'empty dirname'

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
        parent = ''.join(dirname[:-1].rpartition('/')[0:2])
        if state == RET_SUCCESS:
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

    def _handle_remove_dir(self, filed, args):
        """handle client -> mds remove dir request, and response"""
        logging.info('handle remove dir request')

        # get the dirname
        dirname = args['dirname']

        state = RET_SUCCESS
        info = 'ok'

        # check dirname valid
        state, info = self._isvalid_dirname(dirname)

        # check subfiles empty
        if state == RET_SUCCESS:
            if self.mds.hassub(dirname):
                state = RET_FAILURE
                info = 'has subfiles in %s ' + dirname

        # check dir exists
        if state == RET_SUCCESS:
            if not self.mds.hasdir(dirname):
                state = RET_FAILURE
                info = 'directory not exists: ' + dirname

        # write to meta db
        if state == RET_SUCCESS:
            state = self.mds.deldir(dirname)
            if state == RET_FAILURE:
                info = 'rmdir error'

        # reply to client
        reply = RemoveDirReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("remove dir return: %s", msg)
        send_command(filed, msg)

    def _handle_list_dir(self, filed, args):
        """handle client -> mds list dir request, and response"""
        logging.info('handle list dir request')

        # get the dirname
        dirname = args['dirname']

        state = RET_SUCCESS
        info = ''

        # check dirname valid
        state, info = self._isvalid_dirname(dirname)

        # check dir exists
        if state == RET_SUCCESS:
            if not self.mds.hasdir(dirname):
                state = RET_FAILURE
                info = 'directory not exists: ' + dirname

        # get meta from db
        if state == RET_SUCCESS:
            info = self.mds.lsdir(dirname)
            if not info:  # None
                info = []

        # reply to client
        reply = ListDirReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("list dir return: %s", msg)
        send_command(filed, msg)

    def _handle_status_dir(self, filed, args):
        """handle client -> mds status dir request, and response"""
        logging.info('handle status dir request')

        # get the dirname
        dirname = args['dirname']

        state = RET_SUCCESS
        info = ''

        # check dirname valid
        state, info = self._isvalid_dirname(dirname)

        # write to meta db
        if state == RET_SUCCESS:
            dirinfo = self.mds.statdir(dirname)
            if not dirinfo:
                state = RET_FAILURE
                info = 'no such directory'
            else:
                info = dirinfo

        # reply to client
        reply = StatusDirReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("status dir return: %s", msg)
        send_command(filed, msg)

    def _handle_valid_dir(self, filed, args):
        """handle client -> mds valid dir request, and response"""
        logging.info('handle valid dir request')

        # get the dirname
        dirname = args['dirname']

        state = RET_SUCCESS
        info = 'ok'

        # check dirname valid
        state, info = self._isvalid_dirname(dirname)

        # check dir exists
        if state == RET_SUCCESS:
            if not self.mds.hasdir(dirname):
                state = RET_FAILURE
                info = 'directory not exists: ' + dirname

        # reply to client
        reply = ValidDirReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("valid dir return: %s", msg)
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
