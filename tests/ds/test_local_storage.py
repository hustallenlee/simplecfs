# -*- coding: utf-8 -*-
"""
unit test for local_storage module
"""
from nose.tools import eq_

from simplecfs.ds.local_storage import DSStore
from simplecfs.common.parameters import RET_SUCCESS, RET_FAILURE,\
    CHUNK_OK, CHUNK_MISSING


class TestDSStore(object):
    """class to test DSStore"""
    def setup(self):
        data = 'data write into file!'
        ds1 = DSStore('./bin/storage/')
        ret = ds1.write_chunk('test_chunk', data)
        eq_(ret, RET_SUCCESS)

    def teardown(self):
        ds1 = DSStore('./bin/storage/')
        ret = ds1.remove_chunk('test_chunk')
        eq_(ret, RET_SUCCESS)

    def test_init(self):
        ds1 = DSStore()
        eq_(ds1.store_dir, './storage/')

        ds2 = DSStore('./noslash')
        eq_(ds2.store_dir, './noslash/')

        ds3 = DSStore('  ./needstrip/  ')
        eq_(ds3.store_dir, './needstrip/')

    def test_write_chunk(self):
        # correct write test in setup
        data = 'data write into file!'

        # incorrect write
        ds2 = DSStore('./nosuchdir')
        ret = ds2.write_chunk('0_obj2_chk2', data)
        eq_(ret, RET_FAILURE)

    def test_remove_chunk(self):
        # correct remove test in teardown

        # incorret remove
        ds1 = DSStore('./bin/storage/')
        ret = ds1.remove_chunk('nosuchchunk')
        eq_(ret, RET_FAILURE)

        ds2 = DSStore('./nosuchdir/')
        ret = ds2.remove_chunk('nosuchchunk')
        eq_(ret, RET_FAILURE)

    def test_info_chunk(self):
        ds1 = DSStore('./bin/storage/')
        ret = ds1.info_chunk('test_chunk')
        eq_(ret['state'], CHUNK_OK)
        eq_(ret['size'], 21)

        ret = ds1.info_chunk('nosuchchunk')
        eq_(ret['state'], CHUNK_MISSING)
        # assert_less(ret['size'], 0)
        assert ret['size'] < 0

    def test_read_chunk(self):
        ds1 = DSStore('./bin/storage/')
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

    def test_file_size(self):
        ds1 = DSStore('./bin/storage/')
        ret = ds1._file_size('test_chunk')
        eq_(ret, 21)

        ret = ds1._file_size('nosuchchunk')
        assert ret < 0
