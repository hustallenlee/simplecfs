# -*- coding: utf-8 -*-
"""
client api
"""
import logging
import logging.handlers
import eventlet
from os.path import normpath

from simplecfs.message.packet import MakeDirPacket, ListDirPacket,\
    ValidDirPacket, StatusDirPacket, RemoveDirPacket
from simplecfs.message.network_handler import send_command, recv_command
from simplecfs.common.parameters import RET_FAILURE


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

    def putfile(self, src_path, des_path, code_info):
        """put local @src_path file to remote @des_path with @code_info"""
        pass

    def getfile(self, des_path, local_path, repair_flag):
        """get file from @des_path to @local_path,
        if repair_flag is True, repair missing chunks
        """
        pass

    def delfile(self, path):
        """delete a file"""
        pass

    def statfile(self, path):
        """stat a file"""
        pass
