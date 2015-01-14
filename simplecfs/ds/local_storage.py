# -*- coding: utf-8 -*-
"""
handle local storage: write, remove, read and info of data chunk.
"""

import logging
import os

from simplecfs.common.parameters import (RET_SUCCESS, RET_FAILURE,
                                         CHUNK_OK, CHUNK_MISSING)


class DSStore(object):
    """class to handle local chunk operation"""

    def __init__(self, store_dir='./storage/'):
        self.store_dir = store_dir.strip()
        if self.store_dir[-1] != '/':
            self.store_dir += '/'

    def write_chunk(self, chunk_id, chunk_data):
        """store chunk data into local file, named chunk_id,
        """
        try:
            fout = open(self.store_dir+chunk_id, 'wb')
        except IOError:
            logging.exception("open file error")
            return RET_FAILURE
        fout.write(chunk_data)
        fout.close()
        return RET_SUCCESS

    def remove_chunk(self, chunk_id):
        """remove chunk data named chunk_id
        """
        try:
            os.remove(self.store_dir+chunk_id)
        except OSError:
            logging.exception("remove file error")
            return RET_FAILURE
        return RET_SUCCESS

    def info_chunk(self, chunk_id):
        """get information of chunk data named chunk_id,
        return info dict: {'state': OK/MISSING/etc.,
                           'size': ,}
        """
        ret = {}
        ret['state'] = CHUNK_OK
        ret['size'] = self._file_size(chunk_id)
        if ret['size'] < 0:
            ret['state'] = CHUNK_MISSING
        return ret

    def read_chunk(self, chunk_id, block_count, block_list):
        """read several blocks of chunk
        @chunk_ID: the chunk ID, namely the chunk name
        @block_count: the total blocks of one chunk
        @block_list: list of block sequence in the chunk, start of 0
        return: (state, data_list)
        """
        chunk_size = self._file_size(chunk_id)
        if chunk_size < 0:
            return (RET_FAILURE, [])
        block_size = chunk_size / block_count
        fin = open(self.store_dir+chunk_id, 'rb')
        data = []
        for block in block_list:
            fin.seek(block*block_size)
            data.append(fin.read(block_size))
        fin.close()
        return (RET_SUCCESS, data)

    def _file_size(self, chunk_id):
        """get the size of file chunk_id
        return negative number on failure, else return file size
        """
        try:
            state_info = os.stat(self.store_dir+chunk_id)
        except OSError:
            logging.exception("get file size error")
            return -1
        return state_info.st_size
