# -*- coding: utf-8 -*-
"""
unit test for packet module
"""
from nose.tools import eq_

from simplecfs.common.parameters import *   # NOQA
from simplecfs.message.packet import *      # NOQA


def test_pack_unpack():
    """test different data to pack and unpack"""
    source = 'a string'
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)

    source = 1234
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)

    source = {'item': 'test'}
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)

    source = ['item1', 'item2']
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)

    source = True
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)

    source = False
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)

    source = None
    pack_data = pack(source)
    unpack_data = unpack(pack_data)
    eq_(source, unpack_data)


class TestAddChunkPacket(object):
    """the add chunk packet"""
    def test_get_message(self):
        chunk_id = 'ob0_chk1'
        chunk_length = 23
        packet = AddChunkPacket(chunk_id, chunk_length)
        msg = packet.get_message()
        eq_(OP_ADD_CHUNK, msg['method'])
        eq_(chunk_id, msg['chunk_id'])
        eq_(chunk_length, msg['length'])


class TestAddChunkReplyPacket(object):
    """the add chunk packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = AddChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_ADD_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = AddChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_ADD_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestDeleteChunkPacket(object):
    """the delete chunk packet"""
    def test_get_message(self):
        chunk_id = 'ob0_chk1'
        packet = DeleteChunkPacket(chunk_id)
        msg = packet.get_message()
        eq_(OP_DELETE_CHUNK, msg['method'])
        eq_(chunk_id, msg['chunk_id'])


class TestDeleteChunkRePlyPacket(object):
    """the delete chunk reply  packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = DeleteChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_DELETE_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = DeleteChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_DELETE_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestGetChunkPacket(object):
    """the get chunk packet"""
    def test_get_message(self):
        chunk_id = 'ob0_chk1'
        total = 2
        lists = [0, 1]
        packet = GetChunkPacket(chunk_id, total, lists)
        msg = packet.get_message()
        eq_(OP_GET_CHUNK, msg['method'])
        eq_(chunk_id, msg['chunk_id'])
        eq_(total, msg['total'])
        eq_(lists, msg['list'])


class TestGetChunkRePlyPacket(object):
    """the get chunk reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = GetChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_GET_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = GetChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_GET_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestAddDSPacket(object):
    """the add dspacket"""
    def test_get_message(self):
        rack_id = 0
        ds_ip = '127.0.0.1'
        ds_port = 7000
        packet = AddDSPacket(rack_id, ds_ip, ds_port)
        msg = packet.get_message()
        eq_(OP_ADD_DS, msg['method'])
        eq_(rack_id, msg['rack_id'])
        eq_(ds_ip, msg['ds_ip'])
        eq_(ds_port, msg['ds_port'])


class TestAddDSRePlyPacket(object):
    """the add ds reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = AddDSReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_ADD_DS_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = AddDSReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_ADD_DS_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestCheckChunkPacket(object):
    """the check chunk packet"""
    def test_get_message(self):
        chunk_id = 'ob0_chk1'
        packet = CheckChunkPacket(chunk_id)
        msg = packet.get_message()
        eq_(OP_CHECK_CHUNK, msg['method'])
        eq_(chunk_id, msg['chunk_id'])


class TestCheckChunkRePlyPacket(object):
    """the check chunk reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = CheckChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_CHECK_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = CheckChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_CHECK_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestReportDSPacket(object):
    """the report ds packet"""
    def test_get_message(self):
        info = {
            'space': 10240,
            'chunk_num': 78,
        }
        ds_ip = '127.0.0.1'
        ds_port = 7000
        packet = ReportDSPacket(ds_ip, ds_port, info)
        msg = packet.get_message()
        eq_(OP_REPORT_DS, msg['method'])
        eq_(info, msg['info'])


class TestReportDSRePlyPacket(object):
    """the report ds reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = ReportDSReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_REPORT_DS_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = ReportDSReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_REPORT_DS_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestMakeDirPacket(object):
    """the make dir packet"""
    def test_get_message(self):
        dirname = '/testdir/'
        packet = MakeDirPacket(dirname)
        msg = packet.get_message()
        eq_(OP_MAKE_DIR, msg['method'])
        eq_(dirname, msg['dirname'])


class TestMakeDirRePlyPacket(object):
    """the make dir reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = MakeDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_MAKE_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = MakeDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_MAKE_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestRemoveDirPacket(object):
    """the remove dir packet"""
    def test_get_message(self):
        dirname = '/testdir/'
        packet = RemoveDirPacket(dirname)
        msg = packet.get_message()
        eq_(OP_REMOVE_DIR, msg['method'])
        eq_(dirname, msg['dirname'])


class TestRemoveDirRePlyPacket(object):
    """the remove dir reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = RemoveDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_REMOVE_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = RemoveDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_REMOVE_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestListDirPacket(object):
    """the list dir packet"""
    def test_get_message(self):
        dirname = '/testdir/'
        packet = ListDirPacket(dirname)
        msg = packet.get_message()
        eq_(OP_LIST_DIR, msg['method'])
        eq_(dirname, msg['dirname'])


class TestListDirRePlyPacket(object):
    """the list dir reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = ['/me/hello', '/me/dir/']
        packet = ListDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_LIST_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = ListDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_LIST_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestStatusDirPacket(object):
    """the status dir packet"""
    def test_get_message(self):
        dirname = '/testdir/'
        packet = StatusDirPacket(dirname)
        msg = packet.get_message()
        eq_(OP_STATUS_DIR, msg['method'])
        eq_(dirname, msg['dirname'])


class TestStatusDirRePlyPacket(object):
    """the status dir reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = StatusDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_STATUS_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = StatusDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_STATUS_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])


class TestValidDirPacket(object):
    """the valid dir packet"""
    def test_get_message(self):
        dirname = '/testdir/'
        packet = ValidDirPacket(dirname)
        msg = packet.get_message()
        eq_(OP_VALID_DIR, msg['method'])
        eq_(dirname, msg['dirname'])


class TestValidDirRePlyPacket(object):
    """the valid dir reply packet"""
    def test_get_message(self):
        state = RET_SUCCESS
        info = 'test infomation'
        packet = ValidDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_VALID_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])

        state = RET_FAILURE
        info = {'error id': 12, 'error msg': 'test error'}
        packet = ValidDirReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_VALID_DIR_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])
