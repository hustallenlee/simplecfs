# -*- coding: utf-8 -*-
"""
unit test for code drivers
"""
import os
from nose.tools import eq_

from simplecfs.coder.driver import RSDriver, CRSDriver, ZDriver
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


class TestCRSDriver(object):
    """class to test crs code driver"""
    def test_init(self):
        """test init"""
        crs = CRSDriver()
        eq_(4, crs.k)
        eq_(2, crs.m)
        eq_(4, crs.w)
        eq_(512, crs.packet_size)
        eq_(1024, crs.block_size)
        eq_(4096, crs.chunk_size)
        eq_(crs.block_size, crs.get_block_size())
        eq_(crs.block_size*crs.w, crs.get_chunk_size())
        eq_(crs.k+crs.m, crs.get_chunk_num())
        eq_(16384, crs.get_object_size())

        crs = CRSDriver(k=3, m=3, w=8, packet_size=1024, block_size=1024)
        eq_(3, crs.k)
        eq_(3, crs.m)
        eq_(8, crs.w)
        eq_(1024, crs.packet_size)
        eq_(1024, crs.block_size)
        eq_(8192, crs.chunk_size)
        eq_(1024, crs.get_block_size())
        eq_(8192, crs.get_chunk_size())
        eq_(6, crs.get_chunk_num())
        eq_(24576, crs.get_object_size())

    def test_code(self):
        crs = CRSDriver()
        data_len = crs.get_object_size()
        orig_data = os.urandom(data_len)

        # test encodE
        (state, chunks) = crs.encode(orig_data)
        eq_(state, RET_SUCCESS)

        encoded_data = chunks[0]
        eq_(encoded_data, orig_data)

        encoded_parity = chunks[1]

        # test decode
        available_data = []
        available_list = []
        list_len = crs.k * crs.w
        for i in range(0, list_len-1):
            available_data.append(
                encoded_data[i*crs.block_size:(i+1)*crs.block_size])
            available_list.append(i)
        available_data.append(encoded_parity[:crs.block_size])
        available_list.append(list_len)

        (state, decoded_data) = crs.decode(available_data, available_list)
        eq_(state, RET_SUCCESS)
        eq_(decoded_data, orig_data)

        # test repair
        repair_indexes = []
        repair_indexes.append(list_len-1)
        for i in range(1, crs.m*crs.w):
            repair_indexes.append(i+list_len)

        exclude_indexes = []
        (state, available_list) = crs.repair_needed_blocks(repair_indexes,
                                                           exclude_indexes)
        eq_(state, RET_SUCCESS)

        available_data = []
        for i in available_list:
            if i < list_len:
                available_data.append(
                    encoded_data[i*crs.block_size:(i+1)*crs.block_size])
            else:
                available_data.append(
                    encoded_parity[(i-list_len)*crs.block_size:
                                   (i-list_len+1)*crs.block_size])

        (state, repair_data) = crs.repair(available_data,
                                          available_list, repair_indexes)
        eq_(state, RET_SUCCESS)
        eq_(encoded_data[(list_len-1)*crs.block_size:],
            repair_data[:crs.block_size])
        eq_(encoded_parity[crs.block_size:], repair_data[crs.block_size:])


class TestZDriver(object):
    """class to test zcode driver"""
    def test_init(self):
        """test init"""
        z = ZDriver()
        eq_(4, z.k)
        eq_(2, z.m)
        eq_(8, z.r)
        eq_(512, z.packet_size)
        eq_(1024, z.block_size)
        eq_(8192, z.chunk_size)
        eq_(z.block_size, z.get_block_size())
        eq_(z.block_size*z.r, z.get_chunk_size())
        eq_(z.k+z.m, z.get_chunk_num())
        eq_(32768, z.get_object_size())

        z = ZDriver(k=3, m=3, packet_size=1024, block_size=1024)
        eq_(3, z.k)
        eq_(3, z.m)
        eq_(9, z.r)
        eq_(1024, z.packet_size)
        eq_(1024, z.block_size)
        eq_(9216, z.chunk_size)
        eq_(1024, z.get_block_size())
        eq_(9216, z.get_chunk_size())
        eq_(6, z.get_chunk_num())
        eq_(27648, z.get_object_size())

    def test_code(self):
        z = ZDriver()
        data_len = z.get_object_size()
        orig_data = os.urandom(data_len)

        # test encode
        (state, chunks) = z.encode(orig_data)
        eq_(state, RET_SUCCESS)

        encoded_data = chunks[0]
        eq_(encoded_data, orig_data)

        encoded_parity = chunks[1]

        # test decode
        available_data = []
        available_list = []

        list_len = z.k * z.r
        for i in range(0, list_len):
            available_data.append(
                encoded_data[i*z.block_size:(i+1)*z.block_size])
            available_list.append(i)

        (state, decoded_data) = z.decode(available_data, available_list)
        eq_(state, RET_SUCCESS)
        eq_(decoded_data, orig_data)

        # test repair
        repair_chunk = 0

        exclude_indexes = []
        (state, available_list) = z.repair_needed_blocks(repair_chunk,
                                                         exclude_indexes)
        eq_(state, RET_SUCCESS)

        available_data = []
        for i in available_list:
            if i < list_len:
                available_data.append(
                    encoded_data[i*z.block_size:(i+1)*z.block_size])
            else:
                available_data.append(
                    encoded_parity[(i-list_len)*z.block_size:
                                   (i-list_len+1)*z.block_size])

        (state, repair_data) = z.repair(available_data,
                                        available_list, repair_chunk)
        eq_(state, RET_SUCCESS)
        eq_(encoded_data[:z.chunk_size], repair_data)
