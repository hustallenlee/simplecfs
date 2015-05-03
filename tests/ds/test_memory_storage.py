# -*- coding: utf-8 -*-
"""
unit test for memory_storage module
"""
from nose.tools import eq_

from simplecfs.ds.memory_storage import MemStore
from simplecfs.common.parameters import RET_SUCCESS, RET_FAILURE,\
    CHUNK_OK, CHUNK_MISSING


class TestMemStore(object):
    """class to test MemStore"""

    def test_memstore(self):
        data = 'data write into file!'
        ds1 = MemStore()
        ret = ds1.write_chunk('test_chunk', data)
        eq_(ret, RET_SUCCESS)

        ret = ds1.info_chunk('test_chunk')
        eq_(ret['state'], CHUNK_OK)
        eq_(ret['size'], 21)

        ret = ds1.info_chunk('nosuchchunk')
        eq_(ret['state'], CHUNK_MISSING)
        assert ret['size'] < 0

        ret = ds1.read_chunk('test_chunk', 3, [0, 1])
        eq_(ret[0], RET_SUCCESS)
        eq_(ret[1], ['data wr', 'ite int'])

        ret = ds1.read_chunk('test_chunk', 3, [2, 1])
        eq_(ret[0], RET_SUCCESS)
        eq_(ret[1], ['o file!', 'ite int'])

        ret = ds1.read_chunk('nosuchchunk', 3, [0, 1])
        eq_(ret[0], RET_FAILURE)
        eq_(ret[1], [])

        ret = ds1.read_chunk('test_chunk', 0, [0, 1])
        eq_(ret[0], RET_FAILURE)

        ret = ds1._file_size('test_chunk')
        eq_(ret, 21)

        ret = ds1._file_size('nosuchchunk')
        assert ret < 0

        ret = ds1.remove_chunk('test_chunk')
        eq_(ret, RET_SUCCESS)
