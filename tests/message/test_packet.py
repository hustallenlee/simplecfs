# -*- coding: utf-8 -*-
"""
unit test for packet module
"""
from nose.tools import eq_

from simplecfs.common.parameters import OP_ADD_CHUNK, OP_ADD_CHUNK_REPLY,\
    RET_SUCCESS, RET_FAILURE, OP_DELETE_CHUNK, OP_DELETE_CHUNK_REPLY,\
    OP_GET_CHUNK, OP_GET_CHUNK_REPLY
from simplecfs.message.packet import pack, unpack, AddChunkPacket,\
    AddChunkReplyPacket, DeleteChunkPacket, DeleteChunkReplyPacket,\
    GetChunkPacket, GetChunkReplyPacket


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
        packet = DeleteChunkReplyPacket(state, info)
        msg = packet.get_message()
        eq_(OP_DELETE_CHUNK_REPLY, msg['method'])
        eq_(state, msg['state'])
        eq_(info, msg['info'])
