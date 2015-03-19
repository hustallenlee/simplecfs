# -*- coding: utf-8 -*-
"""
mds network server and the main controller
"""
import eventlet
import logging
import time
import socket
import random

from simplecfs.mds.meta_storage import MDSStore
from simplecfs.message.network_handler import recv_command, send_command
from simplecfs.common.parameters import RET_SUCCESS, RET_FAILURE, OP_MAKE_DIR,\
    OP_REMOVE_DIR, OP_LIST_DIR, OP_STATUS_DIR, OP_VALID_DIR, OP_ADD_DS,\
    OP_REPORT_DS, DS_CONNECTED, DS_BROKEN, OP_ADD_FILE, OP_ADD_FILE_COMMIT,\
    OP_STAT_FILE, OP_DELETE_FILE, CODE_CRS, CODE_RS, CODE_Z, CHUNK_OK
from simplecfs.message.packet import MakeDirReplyPacket, RemoveDirReplyPacket,\
    ListDirReplyPacket, StatusDirReplyPacket, ValidDirReplyPacket,\
    AddDSReplyPacket, ReportDSReplyPacket, AddFileReplyPacket,\
    AddFileCommitReplyPacket, StatFileReplyPacket, DeleteFileReplyPacket
from simplecfs.coder.driver import RSDriver, CRSDriver, ZDriver


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
        expire_time = config.getint('redis', 'expire_time')
        logging.info('set redis host:ip db: %s:%d %d', redis_host,
                     redis_port, redis_db)
        self.mds = MDSStore(host=redis_host, port=redis_port, db=redis_db,
                            expire_time=expire_time)

        self._handlers = {
            OP_ADD_DS: self._handle_add_ds,
            OP_REPORT_DS: self._handle_report_ds,
            OP_MAKE_DIR: self._handle_make_dir,
            OP_REMOVE_DIR: self._handle_remove_dir,
            OP_LIST_DIR: self._handle_list_dir,
            OP_STATUS_DIR: self._handle_status_dir,
            OP_VALID_DIR: self._handle_valid_dir,
            OP_ADD_FILE: self._handle_add_file,
            OP_ADD_FILE_COMMIT: self._handle_add_file_commit,
            OP_STAT_FILE: self._handle_stat_file,
            OP_DELETE_FILE: self._handle_delete_file,
        }

        self._code_map = {
            CODE_RS: RSDriver,
            CODE_CRS: CRSDriver,
            CODE_Z: ZDriver,
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

    def _get_code_driver(self, args):
        """return a init code driver according to args """
        block_size = int(args['block_size'])
        code_info = args['code']
        code_type = code_info['type']

        code = None
        if code_type == CODE_RS:
            logging.info('code type rs')
            k = int(code_info['k'])
            m = int(code_info['m'])
            w = int(code_info['w'])
            packet_size = int(code_info['packet_size'])
            code = RSDriver(k=k, m=m, w=w, packet_size=packet_size,
                            block_size=block_size)
        elif code_type == CODE_CRS:
            logging.info('code type crs')
            k = int(code_info['k'])
            m = int(code_info['m'])
            w = int(code_info['w'])
            packet_size = int(code_info['packet_size'])
            code = CRSDriver(k=k, m=m, w=w, packet_size=packet_size,
                             block_size=block_size)
        elif code_type == CODE_Z:
            logging.info('code type zcode')
            k = int(code_info['k'])
            m = int(code_info['m'])
            packet_size = int(code_info['packet_size'])
            code = ZDriver(k=k, m=m, packet_size=packet_size,
                           block_size=block_size)
        return code

    def _assign_ds(self, alive_ds, object_num, chunk_num):
        """assign ds to chunks
        alive_ds: ["ip:port", "ip:port", ... ]
        object_num: 4(int)
        chunk_num: 4(int)
        return: [
                    ["ip:port", "ip:port", ..., ],
                    ["ip:port", "ip:port", ..., ],
                    ...,
                ]
        """
        objects = []
        for i in range(0, object_num):
            chunks = random.sample(alive_ds, chunk_num)
            objects.append(chunks)

        return objects

    def _handle_add_file(self, filed, args):
        """handle client -> mds add file request, store to tmp table,
        and response,
        """
        logging.info('handle add file request')

        state = RET_SUCCESS
        info = ''

        # get the file name, file size
        filename = args['name']
        fileinfo = args['info']
        # TODO: check file exists or not

        try:
            # set the code driver by fileinfo
            code = self._get_code_driver(fileinfo)
        except (KeyError, ValueError, AssertionError):
            logging.exception('set code driver error')
            state = RET_FAILURE
            info = 'code info error'

        file_info = {}
        if state == RET_SUCCESS:
            # count the object num according to object size and file size
            object_size = code.get_object_size()
            filesize = int(fileinfo['filesize'])
            object_num = int(filesize/object_size)
            if filesize % object_size:   # add puls one
                object_num += 1
            chunk_num = code.get_chunk_num()

            file_info['filename'] = filename
            file_info['filesize'] = filesize
            file_info['code'] = fileinfo['code']
            file_info['object_num'] = object_num
            file_info['object_size'] = object_size
            file_info['block_size'] = code.get_block_size()
            file_info['chunk_size'] = code.get_chunk_size()
            file_info['chunk_num'] = chunk_num

            # check the ds alive num, must > chunk num(k+m)
            alive_ds = self.mds.get_alive_ds()
            if len(alive_ds) < code.get_chunk_num():
                logging.error('alive ds num (%d) must not less than '
                              'chunk num (%d) in one stripe',
                              len(alive_ds), code.get_chunk_num())
                state = RET_FAILURE
                info = 'alive ds num less than chunk num'

            # assign the chunks to alive ds
            objects = self._assign_ds(alive_ds, object_num, chunk_num)
            file_info['objects'] = objects
            if not objects:
                logging.error('assign ds failed')
                state = RET_FAILURE

        if state == RET_SUCCESS:
            # store file meta data to temp table
            self.mds.addtmp(filename, file_info)

        if state == RET_SUCCESS:
            info = file_info

        # response to client
        reply = AddFileReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("add file return: %s", msg)
        send_command(filed, msg)

    def _get_objkey_from_index(self, filename, index):
        return '%s_obj%d' % (filename, index)

    def _get_chkkey_from_index(self, filename, obj_index, chk_index):
        return '%s_obj%d_chk%d' % (filename, obj_index, chk_index)

    def _store_file_info(self, filename, tmpinfo):
        """store file info to seperate tables"""
        # store file info to file table
        file_info = {}
        file_info['filename'] = tmpinfo['filename']
        file_info['filesize'] = tmpinfo['filesize']
        file_info['create_time'] = time.asctime()
        file_info['code'] = tmpinfo['code']
        file_info['object_num'] = tmpinfo['object_num']
        file_info['object_size'] = tmpinfo['object_size']
        file_info['block_size'] = tmpinfo['block_size']

        ret = self.mds.addfile(filename, file_info)
        if ret == RET_FAILURE:
            logging.error('mds add file error')

        object_num = tmpinfo['object_num']
        chunk_size = tmpinfo['chunk_size']
        chunk_num = tmpinfo['chunk_num']
        block_size = tmpinfo['block_size']

        # store objects info to object table
        if ret == RET_SUCCESS:
            object_info = {}
            object_info['code'] = tmpinfo['code']
            object_info['object_size'] = tmpinfo['object_size']
            object_info['chunk_num'] = chunk_num
            object_info['block_size'] = block_size
            for i in range(0, object_num):
                object_id = self._get_objkey_from_index(filename, i)
                ret = self.mds.addobj(object_id, object_info)
                if ret == RET_FAILURE:
                    logging.error('add object error')
                    break

        # store chunk info to chunk table
        if ret == RET_SUCCESS:
            chunk_id = ''
            chunk_info = {}
            chunk_info['chunk_size'] = chunk_size
            chunk_info['block_size'] = block_size
            chunk_info['block_num'] = int(chunk_size/block_size)
            chunk_info['status'] = CHUNK_OK

            objects = tmpinfo['objects']
            for obj_index in range(0, object_num):
                for chk_index in range(0, chunk_num):
                    chunk_id = self._get_chkkey_from_index(filename,
                                                           obj_index,
                                                           chk_index)
                    chunk_info['ds_id'] = objects[obj_index][chk_index]
                    ret = self.mds.addchk(chunk_id, chunk_info)

        return ret

    def _handle_add_file_commit(self, filed, args):
        """handle client -> mds add file commit request, and response"""
        logging.info('handle add file commit request')

        state = RET_SUCCESS
        info = 'ok'

        # get the filename
        filename = args['name']

        # check if filename in tmp table
        if not self.mds.hastmp(filename):
            state = RET_FAILURE
            info = 'time out!! no such file, can not commit'

        # move tmp filename information to real table
        tmpinfo = self.mds.gettmp(filename)
        state = self._store_file_info(filename, tmpinfo)

        # delete tmp filename information
        if state == RET_SUCCESS:
            self.mds.deltmp(filename)

        # reply to client
        reply = AddFileCommitReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("add file commit return: %s", msg)
        send_command(filed, msg)

    def _handle_stat_file(self, filed, args):
        """handle client -> mds stat file request, and response"""
        logging.info('handle stat file request')

        state = RET_SUCCESS
        info = 'ok'

        # reply to client
        reply = StatFileReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("stat file return: %s", msg)
        send_command(filed, msg)

    def _handle_delete_file(self, filed, args):
        """handle client -> mds delete file request, and response"""
        logging.info('handle delete file request')

        state = RET_SUCCESS
        info = 'ok'

        # reply to client
        reply = DeleteFileReplyPacket(state, info)
        msg = reply.get_message()
        logging.info("delete file return: %s", msg)
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
