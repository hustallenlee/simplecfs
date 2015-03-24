# -*- coding: utf-8 -*-
"""
client api
"""
import logging
import logging.handlers
import eventlet
from os.path import normpath, getsize

from simplecfs.message.packet import MakeDirPacket, ListDirPacket,\
    ValidDirPacket, StatusDirPacket, RemoveDirPacket, AddFilePacket,\
    AddChunkPacket, AddFileCommitPacket, StatFilePacket, DeleteFilePacket,\
    DeleteChunkPacket
from simplecfs.coder.driver import RSDriver, CRSDriver, ZDriver
from simplecfs.message.network_handler import send_command, recv_command,\
    send_data
from simplecfs.common.parameters import RET_FAILURE, RET_SUCCESS, CODE_RS,\
    CODE_CRS, CODE_Z


class Client(object):
    """client to do request"""
    def __init__(self, config, test=False):
        """
        @config: ConfigParser() object
        @test: for unit test purpose
        """
        self._config = config

        # init logging
        logger = logging.getLogger()  # get the 'root' logger
        level = getattr(logging, config.get('log', 'log_level'))
        logger.setLevel(level)
        log_name = config.get('log', 'log_name')
        log_max_bytes = config.getint('log', 'log_max_bytes')
        log_file_num = config.getint('log', 'log_file_num')
        handler = logging.handlers.RotatingFileHandler(log_name,
                                                       maxBytes=log_max_bytes,
                                                       backupCount=log_file_num)
        log_format = logging.Formatter('%(levelname)-8s[%(asctime)s.%(msecs)d]'
                                       '<%(module)s> %(funcName)s:%(lineno)d:'
                                       ' %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(log_format)
        logger.addHandler(handler)

        # init mds information
        self._mds_ip = config.get('mds', 'mds_ip')
        self._mds_port = config.getint('mds', 'mds_port')

        # init file information
        self._packet_size = config.get('file', 'packet_size')
        self._block_size = config.get('file', 'block_size')

        # init current working directory
        self._cwd = '/'

    def _get_sockfd_to_mds(self):
        sock = eventlet.connect((self._mds_ip, self._mds_port))
        return sock.makefile('rw')

    def _get_sockfd_to_ds(self, ds_ip, ds_port):
        sock = eventlet.connect((ds_ip, ds_port))
        return sock.makefile('rw')

    def _get_objkey_from_idx(self, filename, index):
        return '%s_obj%d' % (filename, index)

    def _get_chkkey_from_idx(self, filename, obj_index, chk_index):
        return '%s_obj%d_chk%d' % (filename, obj_index, chk_index)

    def _change_to_absolute_path(self, pathname):
        """change the path to absolute path in case of relative pathname"""
        # if not absolute path, add _cwd
        if not pathname.startswith('/'):
            pathname = self._cwd + pathname

        # delete '.' and '..'
        pathname = normpath(pathname)

        return pathname

    def mkdir(self, dirname):
        """make directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = MakeDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('mkdir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('mkdir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('mkdir response error: %s', info)
        return (state, info)

    def rmdir(self, dirname):
        """remove empty directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # check current directory in dirname
        if self._cwd.startswith(absolute_path):
            logging.info('can not remove directory contain cwd')
            state = RET_FAILURE
            info = 'can not remvoe directory contain cwd'
            return (state, info)

        # make request packet
        packet = RemoveDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('rmdir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('rmdir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('rmdir response error: %s', info)
        return (state, info)

    def listdir(self, dirname):
        """ls directory
        return: (state, subfiles)
            state: RET_FAILURE/RET_SUCCESS
            subfiles: [file1, dir1, ...]
        """
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = ListDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('list dir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('list dir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('list dir response error: %s', info)
        return (state, info)

    def chdir(self, dirname):
        """change directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = ValidDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('valid dir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('valid dir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('change dir error: %s', info)
        else:
            logging.info('change to dir: %s', absolute_path)
            self._cwd = absolute_path
        return (state, info)

    def getcwd(self):
        """get current working directory"""
        return self._cwd

    def statdir(self, dirname):
        """stat directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = StatusDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('stat dir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('stat dir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('stat dir response error: %s', info)
        return (state, info)

    def _get_code_driver(self, code_info):
        """return a init code driver according to code_info """
        block_size = int(code_info['block_size'])
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

    def _send_chunk_to_ds(self, chunk_id, chunk_data, ds_id):
        packet = AddChunkPacket(chunk_id, len(chunk_data))
        msg = packet.get_message()
        sock = self._get_sockfd_to_ds(ds_id.split(':')[0],
                                      int(ds_id.split(':')[1]))
        send_command(sock, msg)

        # sending data
        send_data(sock, chunk_data)
        recv = recv_command(sock)
        logging.info('send chunk to ds recv: %s', recv)
        sock.close()
        return recv['state']

    def _add_file_commit(self, filename):
        """call after add file"""
        state = RET_SUCCESS
        info = 'ok'

        packet = AddFileCommitPacket(filename)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('add file commit :%s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('add file commit recv: %s', recv)
        sock.close()
        state = recv['state']
        if state == RET_FAILURE:
            info = 'add file commit error'

        return (state, info)

    def putfile(self, src_path, des_path, code_info={}):
        """put local @src_path file to remote @des_path with @code_info"""
        state = RET_SUCCESS
        info = 'ok'

        # get the local src_path information(filesize)
        try:
            filesize = getsize(src_path)
        except OSError:
            logging.error('no such file in local: %s', src_path)
            state = RET_FAILURE
            info = 'no such file in local'

        # get the block_size from config
        block_size = self._config.getint('file', 'block_size')

        # set the fileinfo
        fileinfo = {}
        fileinfo['filesize'] = filesize
        fileinfo['block_size'] = block_size

        code = {  # default code info
            'type': CODE_RS,
            'k': 2,
            'm': 2,
            'w': 8,
            'packet_size': 512,
            'block_size': block_size,
        }
        for (key, value) in code_info.items():
            code[key] = value
        fileinfo['code'] = code

        # call add file to mds with des_path and fileinfo
        filename = self._change_to_absolute_path(des_path)
        packet = AddFilePacket(filename, fileinfo)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('put file send to mds: %s', msg)
        send_command(sock, msg)

        # recv the mds response
        recv = recv_command(sock)
        sock.close()
        logging.info('put file recv from mds: %s', recv)

        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.error('put file recv from mds error')
            return (state, info)

        # get the objects and chunks ds information
        object_size = info['object_size']
        object_num = info['object_num']
        chunk_size = info['chunk_size']
        ds_list = info['objects']
        driver = self._get_code_driver(code)
        fd = open(src_path, 'r')

        for obj_idx in range(object_num):
            # split file to object
            data = fd.read(object_size)
            if len(data) < object_size:
                data += ' ' * (object_size - len(data))

            # encode object to chunks
            (state, chunks) = driver.encode(data)
            if state == RET_FAILURE:
                logging.error('driver encode error')
                info = 'driver encode error'
                return (state, info)

            data_chunk_num = driver.get_data_chunk_num()
            parity_chunk_num = driver.get_parity_chunk_num()
            # put chunks to ds
            for data_idx in range(data_chunk_num):
                chunk_id = self._get_chkkey_from_idx(filename,
                                                     obj_idx,
                                                     data_idx)
                chunk_data = chunks[0][data_idx*chunk_size:
                                       (data_idx+1)*chunk_size]
                ds_id = ds_list[obj_idx][data_idx]
                self._send_chunk_to_ds(chunk_id, chunk_data, ds_id)

            for parity_idx in range(parity_chunk_num):
                chunk_id = self._get_chkkey_from_idx(filename,
                                                     obj_idx,
                                                     parity_idx+data_chunk_num)
                chunk_data = chunks[1][parity_idx*chunk_size:
                                       (parity_idx+1)*chunk_size]
                ds_id = ds_list[obj_idx][parity_idx+data_chunk_num]
                self._send_chunk_to_ds(chunk_id, chunk_data, ds_id)

        fd.close()

        # commit to mds
        if state == RET_SUCCESS:
            (state, info) = self._add_file_commit(filename)

        return (state, info)

    def getfile(self, des_path, local_path, repair_flag):
        """get file from @des_path to @local_path,
        if repair_flag is True, repair missing chunks
        """
        pass

    def delfile(self, path):
        """delete a file"""
        filename = self._change_to_absolute_path(path)

        # delete meta data in mds
        packet = DeleteFilePacket(filename)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('stat file send to mds: %s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('stat file recv %s', recv)
        sock.close()
        state = recv['state']
        info = recv['info']

        # delete data chunk in ds
        for item in info:
            chunk_id = item[0]
            ds_id = item[1]

            packet = DeleteChunkPacket(chunk_id)
            msg = packet.get_message()
            sock = self._get_sockfd_to_ds(ds_id.split(':')[0],
                                          int(ds_id.split(':')[1]))
            send_command(sock, msg)
            recv = recv_command(sock)
            state = recv['state']
            if state == RET_FAILURE:
                logging.error('delete chunk in ds: %s %s', chunk_id, ds_id)
                info = 'delete chunk ds error'

        return (state, info)

    def statfile(self, path):
        """stat a file"""
        filename = self._change_to_absolute_path(path)
        packet = StatFilePacket(filename)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('stat file send to mds: %s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('stat file recv %s', recv)
        sock.close()
        state = recv['state']
        info = recv['info']
        return (state, info)
