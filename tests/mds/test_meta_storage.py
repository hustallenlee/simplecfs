# -*- coding: utf-8 -*-
"""
unit test for meta_storage module
"""
from nose.tools import eq_

from simplecfs.mds.meta_storage import MDSStore


class TestMDSStore(object):
    """class to test MDSStore"""
    def test_set(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        key = 'dir:/mydir/'
        value = {
            'parent_dir': '/',
            'create_time': '2015-03-04'
        }
        ret = mds.set(key, value)
        eq_(ret, True)

    def test_get(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        key = 'dir:/mydir/'
        value = {
            'parent_dir': '/',
            'create_time': '2015-03-04'
        }
        ret = mds.set(key, value)
        eq_(ret, True)

        ret = mds.get(key)
        eq_(ret, value)

    def test_delete(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        key = 'dir:/mydir/'
        value = {
            'parent_dir': '/',
            'create_time': '2015-03-04'
        }
        ret = mds.set(key, value)
        eq_(ret, True)

        ret = mds.delete(key)
        print 'ret: ',
        print ret
        eq_(ret, True)

        ret = mds.delete('nosuchkey')
        print 'ret: ',
        print ret
        eq_(ret, False)

    def test_exists(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        key = 'dir:/mydir/'
        value = {
            'parent_dir': '/',
            'create_time': '2015-03-04'
        }
        ret = mds.set(key, value)
        eq_(ret, True)

        ret = mds.exists(key)
        eq_(ret, True)

        ret = mds.exists('nosuchkey')
        eq_(ret, False)