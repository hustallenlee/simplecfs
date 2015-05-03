# -*- coding: utf-8 -*-
"""
handle memory storage: write, remvoe, read and info of data chunk in memory.
"""
import logging

from simplecfs.common.parameters import RET_SUCCESS, RET_FAILURE,\
    CHUNK_OK, CHUNK_MISSING


class MemStore(object):
    """class to handle memory chunk operations"""
    def __init__(self, store_dir='./storage/'):
        """
        init memory store dict, no use of store_dir,
        data store in dict: store = {
            "chunk_id": "data",
            etc.
        }
        """
        self.store = {}

    def write_chunk(self, chunk_id, chunk_data):
        """store chunk data into memory dict, named chunk_id,
        """
        if chunk_id in self.store:
            logging.error('chunk_id:%s already exists', chunk_id)
            return RET_FAILURE
        self.store[chunk_id] = chunk_data
        return RET_SUCCESS

    def remove_chunk(self, chunk_id):
        """remove chunk data named chunk_id
        """
        try:
            self.store.pop(chunk_id)
        except KeyError:
            logging.exception('chunk_id:%s is not exists', chunk_id)
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
        state: RET_FAILURE/RET_SUCCESS
        data_list: ['block0', 'block1', etc.]
        """
        chunk_size = self._file_size(chunk_id)
        if chunk_size < 0:
            return (RET_FAILURE, [])

        if block_count <= 0:
            return (RET_FAILURE, [])
        block_size = chunk_size / block_count

        chunk_data = self.store[chunk_id]
        data = []
        for block in block_list:
            data.append(chunk_data[block*block_size:(block+1)*block_size])
        return (RET_SUCCESS, data)

    def _file_size(self, chunk_id):
        """get the size of file chunk_id
        return negative number on failure, else return file size
        """
        try:
            data = self.store[chunk_id]
        except KeyError:
            logging.exception("no such chunk_id:%s", chunk_id)
            return -1
        return len(data)
