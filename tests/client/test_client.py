# -*- coding: utf-8 -*-
"""
unit test for client
"""
import ConfigParser as configparser
import eventlet
import tempfile
import os
from nose.tools import eq_

from simplecfs.mds.server import MDSServer
from simplecfs.ds.server import DSServer
from simplecfs.client.api import Client
from simplecfs.common.parameters import *  # NOQA

MDS_CONFIG_FILE = './conf/mds.cfg'
MDS_PORT = '8001'
DS_CONFIG_FILE = './conf/ds.cfg'
DS_PORT = ['7001', '7002', '7003', '7004', '7005']
CLIENT_CONFIG_FILE = './conf/client.cfg'
POOL = eventlet.GreenPool(10)


def start_mds(mds):
    print 'start mds server'
    mds.start()


def init_mds():
    config = configparser.ConfigParser()
    config.read(MDS_CONFIG_FILE)
    config.set('mds', 'mds_port', MDS_PORT)
    mds = MDSServer(config, test=True)
    POOL.spawn_n(start_mds, mds)


def start_ds(ds_):
    print 'start ds server'
    ds_.start()


def init_ds():
    config = configparser.ConfigParser()
    config.read(DS_CONFIG_FILE)
    config.set('mds', 'mds_port', MDS_PORT)
    config.set('storage', 'chunk_store_dir', './bin/storage/')
    for port in DS_PORT:
        config.set('dataserver', 'ds_port', port)
        ds = DSServer(config)
        POOL.spawn_n(start_ds, ds)


def init_client():
    config = configparser.ConfigParser()
    config.read(CLIENT_CONFIG_FILE)
    config.set('mds', 'mds_port', MDS_PORT)

    client = Client(config)
    return client


def directory(client):
    ret = client.getcwd()
    eq_(ret, '/')

    dirname = '/testdir/'
    ret = client.mkdir(dirname)
    eq_(ret[0], True)

    ret = client.listdir('/')
    eq_(ret[0], True)
    eq_(dirname in ret[1], True)

    ret = client.listdir(dirname)
    eq_(ret[0], True)
    eq_(ret[1], [])

    ret = client.statdir('nosuchdir/')
    eq_(ret[0], False)

    ret = client.statdir(dirname)
    eq_(ret[0], True)

    ret = client.chdir(dirname)
    eq_(ret[0], True)
    ret = client.getcwd()
    eq_(ret, dirname)
    ret = client.rmdir(dirname)
    eq_(ret[0], False)

    ret = client.chdir('/')
    eq_(ret[0], True)
    ret = client.getcwd()
    eq_(ret, '/')

    ret = client.rmdir(dirname)
    eq_(ret[0], True)

    ret = client.statdir(dirname)
    eq_(ret[0], False)

    ret = client.chdir(dirname)
    eq_(ret[0], False)
    ret = client.getcwd()
    eq_(ret, '/')


def get_tmpfile(data_length):
    data = os.urandom(data_length)
    filepath = tempfile.mkstemp()[1]
    fd = open(filepath, 'w')
    fd.write(data)
    fd.close()
    return filepath


def rs(client):
    des_path = '/rstest.txt'
    src_length = 2048
    src_path = get_tmpfile(src_length)
    src_data = open(src_path, 'r').read()
    code_info = {  # default code info
        'type': CODE_RS,
        'k': 2,
        'm': 2,
        'w': 8,
        'packet_size': 512,
        'block_size': 1024,
    }
    ret = client.putfile(src_path, des_path, code_info)
    os.remove(src_path)
    eq_(ret[0], True)
    ret = client.statfile(des_path)
    eq_(ret[0], True)
    ret = client.listdir('/')
    eq_(ret[0], True)
    eq_(des_path in ret[1], True)

    # normal read chunk
    chunk_id = '/rstest.txt_obj0_chk0'
    local_chk = tempfile.mkstemp()[1]
    ret = client.getchunk(chunk_id, local_chk)
    eq_(ret[0], True)
    chk_data = open(local_chk, 'r').read()
    os.remove(local_chk)
    eq_(chk_data, src_data[:src_length/2])

    # degrade read chunk
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    ret = client.report_ds(ip, port, DS_BROKEN)
    eq_(ret, True)
    degrade_path = tempfile.mkstemp()[1]
    ret = client.getchunk(chunk_id, degrade_path)
    eq_(ret[0], True)
    degrade_data = open(degrade_path, 'r').read()
    os.remove(degrade_path)
    eq_(chk_data, degrade_data)
    ret = client.report_ds(ip, port, DS_CONNECTED)
    eq_(ret, True)

    # read object
    object_id = '/rstest.txt_obj0'
    local_obj = tempfile.mkstemp()[1]
    ret = client.getobject(object_id, local_obj)
    eq_(ret[0], True)
    obj_data = open(local_obj, 'r').read()
    os.remove(local_obj)
    eq_(obj_data, src_data)

    # read file
    des_path = '/rstest.txt'
    local_path = tempfile.mkstemp()[1]
    ret = client.getfile(des_path, local_path)
    eq_(ret[0], True)
    file_data = open(local_path, 'r').read()
    os.remove(local_path)
    eq_(file_data, src_data)

    # delete file
    ret = client.delfile(des_path)
    eq_(ret[0], True)


def crs(client):
    des_path = '/crstest.txt'
    src_length = 16384
    src_path = get_tmpfile(src_length)
    src_data = open(src_path, 'r').read()
    print 'temp file: %s' % src_path
    code_info = {  # default code info
        'type': CODE_CRS,
        'k': 2,
        'm': 2,
        'w': 8,
        'packet_size': 512,
        'block_size': 1024,
    }
    ret = client.putfile(src_path, des_path, code_info)
    os.remove(src_path)
    eq_(ret[0], True)
    ret = client.statfile(des_path)
    eq_(ret[0], True)
    ret = client.listdir('/')
    eq_(ret[0], True)
    eq_(des_path in ret[1], True)

    # normal read chunk
    chunk_id = '/crstest.txt_obj0_chk0'
    local_chk = tempfile.mkstemp()[1]
    ret = client.getchunk(chunk_id, local_chk)
    eq_(ret[0], True)
    chk_data = open(local_chk, 'r').read()
    os.remove(local_chk)
    eq_(chk_data, src_data[:src_length/2])

    # degrade read chunk
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    ret = client.report_ds(ip, port, DS_BROKEN)
    eq_(ret, True)
    degrade_path = tempfile.mkstemp()[1]
    ret = client.getchunk(chunk_id, degrade_path)
    eq_(ret[0], True)
    degrade_data = open(degrade_path, 'r').read()
    os.remove(degrade_path)
    eq_(chk_data, degrade_data)
    ret = client.report_ds(ip, port, DS_CONNECTED)
    eq_(ret, True)

    # read object
    object_id = '/crstest.txt_obj0'
    local_obj = tempfile.mkstemp()[1]
    ret = client.getobject(object_id, local_obj)
    eq_(ret[0], True)
    obj_data = open(local_obj, 'r').read()
    os.remove(local_obj)
    eq_(obj_data, src_data)

    # read file
    des_path = '/crstest.txt'
    local_path = tempfile.mkstemp()[1]
    ret = client.getfile(des_path, local_path)
    eq_(ret[0], True)
    file_data = open(local_path, 'r').read()
    os.remove(local_path)
    eq_(file_data, src_data)

    # delete file
    ret = client.delfile(des_path)
    eq_(ret[0], True)


def z(client):
    des_path = '/ztest.txt'
    src_length = 4096
    src_path = get_tmpfile(src_length)
    src_data = open(src_path, 'r').read()
    print 'temp file: %s' % src_path
    code_info = {  # default code info
        'type': CODE_Z,
        'k': 2,
        'm': 2,
        'packet_size': 512,
        'block_size': 1024,
    }
    ret = client.putfile(src_path, des_path, code_info)
    os.remove(src_path)
    eq_(ret[0], True)
    ret = client.statfile(des_path)
    eq_(ret[0], True)
    ret = client.listdir('/')
    eq_(ret[0], True)
    eq_(des_path in ret[1], True)

    # normal read chunk
    chunk_id = '/ztest.txt_obj0_chk0'
    local_chk = tempfile.mkstemp()[1]
    ret = client.getchunk(chunk_id, local_chk)
    eq_(ret[0], True)
    chk_data = open(local_chk, 'r').read()
    os.remove(local_chk)
    eq_(chk_data, src_data[:src_length/2])

    # degrade read chunk
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    ret = client.report_ds(ip, port, DS_BROKEN)
    eq_(ret, True)
    degrade_path = tempfile.mkstemp()[1]
    ret = client.getchunk(chunk_id, degrade_path)
    eq_(ret[0], True)
    degrade_data = open(degrade_path, 'r').read()
    os.remove(degrade_path)
    eq_(chk_data, degrade_data)
    ret = client.report_ds(ip, port, DS_CONNECTED)
    eq_(ret, True)

    # read object
    object_id = '/ztest.txt_obj0'
    local_obj = tempfile.mkstemp()[1]
    ret = client.getobject(object_id, local_obj)
    eq_(ret[0], True)
    obj_data = open(local_obj, 'r').read()
    os.remove(local_obj)
    eq_(obj_data, src_data)

    # read file
    des_path = '/ztest.txt'
    local_path = tempfile.mkstemp()[1]
    ret = client.getfile(des_path, local_path)
    eq_(ret[0], True)
    file_data = open(local_path, 'r').read()
    os.remove(local_path)
    eq_(file_data, src_data)

    # delete file
    ret = client.delfile(des_path)
    eq_(ret[0], True)


def test_client():
    init_mds()
    init_ds()
    client = init_client()
    directory(client)
    rs(client)
    crs(client)
    z(client)
