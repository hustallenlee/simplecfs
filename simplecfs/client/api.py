# -*- coding: utf-8 -*-
"""
client api
"""
import logging
import logging.handlers


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

    def mkdir(self, dirname):
        """make directory"""
        pass

    def rmdir(self, dirname):
        """remove empty directory"""
        pass

    def listdir(self, dirname):
        """ls directory"""
        pass

    def chdir(self, path):
        """change directory"""
        pass

    def getcwd(self):
        """get current working directory"""
        return self._cwd

    def statdir(self, dirname):
        """stat directory"""
        pass

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
