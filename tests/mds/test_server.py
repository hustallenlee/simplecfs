# -*- coding: utf-8 -*-
"""
unit test for mds
"""
import ConfigParser as configparser
import logging
import logging.handlers
import eventlet
from nose.tools import eq_

from simplecfs.mds.server import MDSServer
from simplecfs.common.parameters import *  # NOQA
from simplecfs.message.packet import MakeDirPacket, RemoveDirPacket,\
    ListDirPacket, StatusDirPacket, ValidDirPacket, AddDSPacket,\
    ReportDSPacket, AddFilePacket, AddFileCommitPacket, StatFilePacket,\
    DeleteFilePacket, GetFilePacket, GetObjPacket, GetChkPacket,\
    RepairChkPacket, RepairChkCommitPacket
from simplecfs.message.network_handler import send_command, recv_command

MDS_CONFIG_FILE = './conf/mds.cfg'
CLIENT_CONFIG_FILE = './conf/client.cfg'
POOL = eventlet.GreenPool(10)


def start_mds(mds):
    print 'start mds server'
    mds.start()


def get_new_connection():
    # get config options
    config = configparser.ConfigParser()
    config.read(CLIENT_CONFIG_FILE)
    mds_ip = config.get('mds', 'mds_ip')
    mds_port = config.getint('mds', 'mds_port')
    print 'connect to server'
    return eventlet.connect((mds_ip, mds_port))


def make_dir(dirname='/testdir/'):
    """test function: make_dir(dirname)
    dirname should be absolute path and end with '/'
    """

    dirname = dirname.strip()
    if not dirname.endswith('/'):
        dirname += '/'
    print 'make dirname %s' % dirname
    packet = MakeDirPacket(dirname)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def remove_dir(dirname='/testdir/'):
    """test function: remove_dir(dirname)
    dirname should be absolute path and end with '/'
    """

    dirname = dirname.strip()
    if not dirname.endswith('/'):
        dirname += '/'
    print 'remove dirname %s' % dirname
    packet = RemoveDirPacket(dirname)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def list_dir(dirname='/'):
    """test function: list_dir(dirname)
    dirname should be absolute path and end with '/'
    """

    dirname = dirname.strip()
    if not dirname.endswith('/'):
        dirname += '/'
    print 'list dirname %s' % dirname
    packet = ListDirPacket(dirname)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def status_dir(dirname='/testdir/'):
    """test function: status_dir(dirname)
    dirname should be absolute path and end with '/'
    """

    dirname = dirname.strip()
    if not dirname.endswith('/'):
        dirname += '/'
    print 'status dirname %s' % dirname
    packet = StatusDirPacket(dirname)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def valid_dir(dirname='/testdir/'):
    """test function: valid_dir(dirname)
    dirname should be absolute path and end with '/'
    """

    dirname = dirname.strip()
    if not dirname.endswith('/'):
        dirname += '/'
    print 'valid dirname %s' % dirname
    packet = ValidDirPacket(dirname)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7000):
    """test function: add_ds(rack_id, ds_ip, ds_port)
    """
    print 'add ds, rack_id:%d ip:%s port:%d' % (rack_id, ds_ip, ds_port)
    packet = AddDSPacket(rack_id, ds_ip, ds_port)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def report_ds(ds_ip='127.0.0.1', ds_port=7000, status=DS_CONNECTED):
    """test function: report_ds(info)
    report ds state info to mds
    """
    info = {
        'space': 102400,
        'chunk_num': 898,
        'status': status,
    }
    packet = ReportDSPacket(ds_ip, ds_port, info)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def add_file(filename='/testfile', fileinfo={}):
    """
    test function: add_file(filename, fileinfo)
    filename should be absolute path,
    finleinfo contain all the info in dict format:
    fileinfo = {
        "filename": filename,
        "filesize": 1048576,
        "block_size": 512,
        "code": {
            "type": "rs",  # "rs/crs/zcode/etc.",
            "k": 2,
            "m": 2,
            "w": 8,
        },
    }
    """
    fileinfo = {
        "filesize": 20480,
        "code": {
            "type": CODE_RS,  # "rs/crs/zcode/etc.",
            "k": 2,
            "m": 2,
            "w": 8,
            "packet_size": 512,
            "block_size": 1024,
        },
    }

    print 'add file %s' % filename
    print 'file info:'
    print fileinfo
    packet = AddFilePacket(filename, fileinfo)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def add_file_commit(filename='/testfile'):
    """
    test function: add_file_commit(filename)
    filename should be absolute path,
    """
    print 'add file commit %s' % filename
    packet = AddFileCommitPacket(filename)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def stat_file(filename='/testfile'):
    """
    test function: stat_file(filename)
    filename should be absolute path,
    """
    print 'stat file %s' % filename
    packet = StatFilePacket(filename)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def delete_file(filename='/testfile'):
    """
    test function: delete_file(filename)
    filename should be absolute path,
    """
    print 'delete file %s' % filename
    packet = DeleteFilePacket(filename)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def get_file(filepath='/testfile'):
    """
    test function: get_file(filepath)
    filepath should be absolute path,
    """
    print 'get file %s' % filepath
    packet = GetFilePacket(filepath)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def get_obj(obj_id='/testfile_obj0'):
    """
    test function: get_obj(obj_id)
    """
    print 'get obj %s' % obj_id
    packet = GetObjPacket(obj_id)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def get_chk(chk_id='/testfile_obj0_chk0'):
    """
    test function: get_chk(chk_id)
    """
    print 'get chk %s' % chk_id
    packet = GetChkPacket(chk_id)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def repair_chk(chk_id='/testfile_obj0_chk0'):
    """
    test function: repair_chk(chk_id)
    """
    print 'repair chk %s' % chk_id
    packet = RepairChkPacket(chk_id)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def repair_chk_commit(chk_id='/testfile_obj0_chk0',
                      ds_id='127.0.0.1:7000'):
    """
    test function: repair_chk_commit(chk_id, ds_id)
    """
    print 'repair chk commit %s %s' % (chk_id, ds_id)
    packet = RepairChkCommitPacket(chk_id, ds_id)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    return recv


def test_mds():
    # start the mds
    config = configparser.ConfigParser()
    config.read(MDS_CONFIG_FILE)

    # start server
    mds = MDSServer(config, test=True)
    POOL.spawn_n(start_mds, mds)

    # start test mds
    dirname = '/testdir/'
    ret = make_dir(dirname)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_MAKE_DIR_REPLY)

    ret = list_dir('/')
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_LIST_DIR_REPLY)
    eq_(True, dirname in ret['info'])

    ret = list_dir(dirname)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_LIST_DIR_REPLY)
    eq_([], ret['info'])

    ret = status_dir(dirname)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_STATUS_DIR_REPLY)

    ret = status_dir('/nosuchdir/')
    eq_(ret['state'], RET_FAILURE)
    eq_(ret['method'], OP_STATUS_DIR_REPLY)

    ret = valid_dir(dirname)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_VALID_DIR_REPLY)

    ret = valid_dir('/nosuchdir/')
    eq_(ret['state'], RET_FAILURE)
    eq_(ret['method'], OP_VALID_DIR_REPLY)

    ret = remove_dir('/nosuchdir/')
    eq_(ret['state'], RET_FAILURE)
    eq_(ret['method'], OP_REMOVE_DIR_REPLY)

    ret = remove_dir(dirname)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_REMOVE_DIR_REPLY)

    ret = list_dir('/')
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_LIST_DIR_REPLY)
    eq_(False, dirname in ret['info'])

    ret = status_dir(dirname)
    eq_(ret['state'], RET_FAILURE)
    eq_(ret['method'], OP_STATUS_DIR_REPLY)

    ret = valid_dir(dirname)
    eq_(ret['state'], RET_FAILURE)
    eq_(ret['method'], OP_VALID_DIR_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7000)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = report_ds()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_REPORT_DS_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7001)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = report_ds(ds_ip='127.0.0.1', ds_port=7001, status=DS_BROKEN)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_REPORT_DS_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7002)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7003)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7004)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7005)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7006)
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_DS_REPLY)

    ret = add_file()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_FILE_REPLY)

    ret = add_file_commit()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_FILE_COMMIT_REPLY)

    ret = stat_file()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_STAT_FILE_REPLY)

    ret = delete_file()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_DELETE_FILE_REPLY)

    ret = add_file()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_FILE_REPLY)

    ret = add_file_commit()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_ADD_FILE_COMMIT_REPLY)

    ret = get_file()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_GET_FILE_REPLY)

    ret = get_obj()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_GET_OBJ_REPLY)

    ret = get_chk()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_GET_CHK_REPLY)

    ret = repair_chk()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_REPAIR_CHK_REPLY)

    ret = repair_chk_commit()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_REPAIR_CHK_COMMIT_REPLY)

    ret = delete_file()
    eq_(ret['state'], RET_SUCCESS)
    eq_(ret['method'], OP_DELETE_FILE_REPLY)
