# -*- coding: utf-8 -*-
"""
unit test for meta_storage module
"""
from nose.tools import eq_

from simplecfs.mds.meta_storage import MDSStore
from simplecfs.common.parameters import DS_CONNECTED, DS_BROKEN


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

    def test_dir(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        dirname = '/mytestdir/'
        dirinfo = {
            'parent_dir': '/',
            'create_time': '2015-03-04'
        }
        ret = mds.mkdir(dirname, dirinfo)
        eq_(ret, True)

        ret = mds.hasdir(dirname)
        eq_(ret, True)

        ret = mds.hasdir('/nosuchdir/')
        eq_(ret, False)

        ret = mds.hassub('/')
        eq_(ret, True)

        ret = mds.hassub(dirname)
        eq_(ret, False)

        ret = mds.statdir(dirname)
        eq_(ret, dirinfo)

        ret = mds.lsdir('/')
        eq_(dirname in ret, True)

        ret = mds.deldir(dirname)
        eq_(ret, True)

        ret = mds.hasdir(dirname)
        eq_(ret, False)

        ret = mds.lsdir(dirname)
        eq_(dirname in ret, False)

    def test_ds(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        ds_ip = '127.0.0.1'
        ds_port = 7000
        dsinfo = {
            'space': 23223,
            'chunk_num': 87,
            'status': DS_CONNECTED,
        }

        ret = mds.addds(ds_ip, ds_port, dsinfo)
        eq_(ret, True)

        ret = mds.is_alive_ds(ds_ip, ds_port)
        eq_(ret, True)

        ret = mds.get_alive_ds()
        eq_(True, '127.0.0.1:7000' in ret)

        ret = mds.getds(ds_ip, ds_port)
        eq_(ret['chunk_num'], 87)

        ret = mds.hasds(ds_ip, ds_port)
        eq_(ret, True)

        ret = mds.hasds('/nosuchip', 899)
        eq_(ret, False)

        ret = mds.getds(ds_ip, ds_port)
        eq_(ret, dsinfo)

        newinfo = {
            'space': 23323,
            'chunk_num': 88,
            'status': DS_BROKEN,
        }
        ret = mds.updateds(ds_ip, ds_port, newinfo)
        eq_(ret, True)

        ret = mds.is_alive_ds(ds_ip, ds_port)
        eq_(ret, False)

        ret = mds.getds(ds_ip, ds_port)
        eq_(ret['chunk_num'], 88)

        ret = mds.delds(ds_ip, ds_port)
        eq_(ret, True)

        ret = mds.hasds(ds_ip, ds_port)
        eq_(ret, False)

    def test_tmp(self):
        # connet to redis
        mds = MDSStore(host='127.0.0.1', port=6379, db=0)

        tmpname = '/mytesttmp'
        tmpinfo = {
            'parent_tmp': '/',
            'create_time': '2015-03-04'
        }
        ret = mds.addtmp(tmpname, tmpinfo)
        eq_(ret, True)

        ret = mds.hastmp(tmpname)
        eq_(ret, True)

        ret = mds.gettmp(tmpname)
        eq_(tmpinfo, ret)

        ret = mds.hastmp('/nosuchtmp/')
        eq_(ret, False)

        ret = mds.deltmp(tmpname)
        eq_(ret, True)

        ret = mds.hastmp(tmpname)
        eq_(ret, False)
