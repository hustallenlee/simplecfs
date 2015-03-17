# -*- coding: utf-8 -*-
"""
python driver to call librlc
"""
import ctypes
import logging

from simplecfs.common.parameters import RET_FAILURE, RET_SUCCESS


class RSDriver(object):
    """code driver for RS code
    data format:
        block -> chunk -> object
    block: match one row in code matrix
    chunk: match one ds storage unit
    object: several chunk make up a object, they are in one stripe
    """
    def __init__(self, **args):
        """init the rs driver with args"""
        self.k = 4
        self.m = 2
        self.w = 4
        self.packet_size = 512
        self.block_size = 1024

        try:
            for (key, value) in args.items():
                if key == 'k':
                    self.k = int(value)
                elif key == 'm':
                    self.m = int(value)
                elif key == 'w':
                    self.w = int(value)
                elif key == 'packet_size':
                    self.packet_size = int(value)
                elif key == 'block_size':
                    self.block_size = int(value)
        except (TypeError, ValueError):
            logging.exception('invalid args for DSDriver init')

        self.chunk_size = self.block_size
        self.rs = ctypes.CDLL('ext/librlc/librlc.so')

    def get_block_size(self):
        """return the block size"""
        return self.block_size

    def get_chunk_size(self):
        """return the chunk size"""
        return self.chunk_size

    def get_chunk_num(self):
        """return the chunk num in a object"""
        return self.k + self.m

    def get_object_size(self):
        """return the object size"""
        return self.chunk_size * self.k

    def encode(self, data_bytes):
        """encode data len of data_bytes must equal to object_size
        return: (state, chunks)
            state: RET_FAILURE/RET_SUCCESS
            chunks: [data, parity]
        """
        logging.info('RSDriver encode')
        state = RET_SUCCESS
        chunks = []

        data_len = len(data_bytes)
        if data_len != self.get_object_size():
            logging.error('encode data len valid')
            state = RET_FAILURE
            return (state, chunks)

        encoded_data = ctypes.pointer(ctypes.c_char_p())
        encoded_parity = ctypes.pointer(ctypes.c_char_p())
        block_len = ctypes.c_int(1)
        self.rs.librlc_rs_encode(self.k, self.m, self.w, self.packet_size,
                                 data_bytes, data_len,
                                 ctypes.byref(encoded_data),
                                 ctypes.byref(encoded_parity),
                                 ctypes.byref(block_len))

        block_len = block_len.value
        if block_len != self.block_size:
            logging.error('librlc rs encode block %d differ from\
                          block_size %d', block_len, self.block_size)
            state = RET_FAILURE
            return (state, chunks)

        data = ctypes.string_at(encoded_data, self.k*self.chunk_size)
        chunks.append(data)

        parity = ctypes.string_at(encoded_parity, self.m*self.chunk_size)
        chunks.append(parity)

        self.rs.librlc_rs_encode_cleanup(encoded_data, encoded_parity)

        # return value
        return (state, chunks)

    def decode(self, available_data, available_list):
        """
        decode data from available_data in available_list
            available_data: [block0, block1, ...]
            available_list: [0,1, ...]
        return: (state, decoded_data)
            state: RET_FAILURE/RET_SUCCESS
            decoded_data: orig_data
        """
        logging.info('RSDriver decode')
        state = RET_SUCCESS
        decoded_data = ''

        if len(available_list) < self.k:
            logging.error('decode available data num < %d', self.k)
            state = RET_FAILURE
            return (state, decoded_data)

        data = ''.join(available_data)

        Alist = ctypes.c_int * self.k
        data_list = Alist()
        for i in range(0, self.k):
            data_list[i] = available_list[i]

        out_data = ctypes.pointer(ctypes.c_char_p())
        self.rs.librlc_rs_decode(self.k, self.m, self.w, self.packet_size,
                                 data, data_list, self.k, self.block_size,
                                 ctypes.byref(out_data))

        decoded_data = ctypes.string_at(out_data, self.get_object_size())
        self.rs.librlc_rs_decode_cleanup(out_data)

        # return value
        return (state, decoded_data)

    def repair(self, available_data, available_list, repair_indexes):
        """
        repair data in repair_indexes from available_data
            available_data: [block0, block1, ...]
            available_list: [0,1, ...]
            repair_indexes: [k, k+1, ...]
        return: (state, repair_data)
            state: RET_FAILURE/RET_SUCCESS
            repair_data: data (data in a binary array, in the order of indexs)
        """
        logging.info('RSDriver repair')
        state = RET_SUCCESS
        repair_data = ''

        if len(available_list) < self.k:
            logging.error('repair available data num < k(%d)', self.k)
            state = RET_FAILURE
            return (state, repair_data)

        data = ''.join(available_data)

        Alist = ctypes.c_int * self.k
        data_list = Alist()
        for i in range(0, self.k):
            data_list[i] = available_list[i]

        repair_len = len(repair_indexes)
        if repair_len > self.m:
            logging.error('repair indexs > m(%d)', self.m)
            state = RET_FAILURE
            return (state, repair_data)

        Blist = ctypes.c_int * repair_len
        repair_list = Blist()
        for i in range(0, repair_len):
            repair_list[i] = repair_indexes[i]

        out_data = ctypes.pointer(ctypes.c_char_p())
        self.rs.librlc_rs_repair(self.k, self.m, self.w, self.packet_size,
                                 data, data_list, self.k, self.block_size,
                                 repair_list, repair_len,
                                 ctypes.byref(out_data))

        repair_data = ctypes.string_at(out_data, self.block_size*repair_len)
        self.rs.librlc_rs_repair_cleanup(out_data)

        # return value
        return (state, repair_data)

    def repair_needed_blocks(self, repair_indexes, exclude_indexes):
        """blocks needs to repair indexs but not in exclude_indexes
        return: (state, block_list)
            state: RET_FAILURE/RET_SUCCESS
            block_list: [0, 1, ..., k]
        """
        logging.info('repair needed blocks')
        state = RET_SUCCESS
        block_list = []

        n = self.k + self.m
        block_list = [i for i in range(0, n) if i not in repair_indexes]
        block_list = [i for i in block_list if i not in exclude_indexes]

        if len(block_list) < self.k:
            logging.info('block list num < k')
            state = RET_FAILURE

        return (state, block_list[:self.k])
