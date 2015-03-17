# -*- coding: utf-8 -*-
"""
unit test for code drivers
"""
import os
from nose.tools import eq_

from simplecfs.coder.driver import RSDriver
from simplecfs.common.parameters import RET_SUCCESS


class TestRSDriver(object):
    """class to test code driver"""
    def test_init(self):
        """test init"""
        rs = RSDriver()
        eq_(4, rs.k)
        eq_(2, rs.m)
        eq_(4, rs.w)
        eq_(512, rs.packet_size)
        eq_(1024, rs.block_size)
        eq_(1024, rs.chunk_size)
        eq_(rs.block_size, rs.get_block_size())
        eq_(rs.block_size, rs.get_chunk_size())
        eq_(rs.k+rs.m, rs.get_chunk_num())
        eq_(4096, rs.get_object_size())

        rs = RSDriver(k=3, m=3, w=8, packet_size=1024, block_size=1024)
        eq_(3, rs.k)
        eq_(3, rs.m)
        eq_(8, rs.w)
        eq_(1024, rs.packet_size)
        eq_(1024, rs.block_size)
        eq_(1024, rs.chunk_size)
        eq_(1024, rs.get_block_size())
        eq_(1024, rs.get_chunk_size())
        eq_(6, rs.get_chunk_num())
        eq_(3072, rs.get_object_size())

    def test_code(self):
        rs = RSDriver()
        data_len = rs.get_object_size()
        orig_data = os.urandom(data_len)

        # test encode
        (state, chunks) = rs.encode(orig_data)
        eq_(state, RET_SUCCESS)

        encoded_data = chunks[0]
        eq_(encoded_data, orig_data)

        encoded_parity = chunks[1]

        # test decode
        available_data = []
        available_list = []
        for i in range(0, rs.k-1):
            available_data.append(
                encoded_data[i*rs.block_size:(i+1)*rs.block_size])
            available_list.append(i)
        available_data.append(encoded_parity[:rs.block_size])
        available_list.append(rs.k)

        (state, decoded_data) = rs.decode(available_data, available_list)
        eq_(state, RET_SUCCESS)
        eq_(decoded_data, orig_data)

        # test repair
        repair_indexes = []
        repair_indexes.append(rs.k-1)
        for i in range(1, rs.m):
            repair_indexes.append(i+rs.k)

        exclude_indexes = []
        (state, available_list) = rs.repair_needed_blocks(repair_indexes,
                                                          exclude_indexes)
        eq_(state, RET_SUCCESS)

        available_data = []
        for i in available_list:
            if i < rs.k:
                available_data.append(
                    encoded_data[i*rs.block_size:(i+1)*rs.block_size])
            else:
                available_data.append(
                    encoded_parity[(i-rs.k)*rs.block_size:
                                   (i-rs.k+1)*rs.block_size])

        (state, repair_data) = rs.repair(available_data,
                                         available_list, repair_indexes)
        eq_(state, RET_SUCCESS)
        eq_(encoded_data[(rs.k-1)*rs.block_size:],
            repair_data[:rs.block_size])
        eq_(encoded_parity[rs.block_size:], repair_data[rs.block_size:])
