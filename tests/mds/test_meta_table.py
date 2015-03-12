# -*- coding: utf-8 -*-
"""
unit test for meta tables
"""
from nose.tools import eq_

from simplecfs.mds.meta_table import dir_key, sub_key, file_key, obj_key,\
    chk_key, ds_key, ds_alive_key


def test_dir_key():
    dirname = '/testdir/'
    key = dir_key(dirname)
    eq_(key, 'dir:/testdir/')


def test_sub_key():
    dirname = '/testdir/'
    key = sub_key(dirname)
    eq_(key, 'sub:/testdir/')


def test_file_key():
    filename = '/testfile'
    key = file_key(filename)
    eq_(key, 'file:/testfile')


def test_obj_key():
    objname = '/test_obj0'
    key = obj_key(objname)
    eq_(key, 'obj:/test_obj0')


def test_chk_key():
    chkname = '/test_ob0_chk0'
    key = chk_key(chkname)
    eq_(key, 'chk:'+chkname)


def test_ds_key():
    ip = '127.0.0.1'
    port = 7000
    key = ds_key(ip, port)
    eq_(key, 'ds:127.0.0.1:7000')


def test_ds_alive_key():
    key = ds_alive_key()
    eq_(key, 'ds_alive')
