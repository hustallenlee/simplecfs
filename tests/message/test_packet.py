# -*- coding: utf-8 -*-
"""
unit test for packet module
"""
from nose.tools import eq_

from simplecfs.common.parameters import OP_ADD_CHUNK, OP_ADD_CHUNK_REPLY,\
    RET_SUCCESS, RET_FAILURE
from simplecfs.message.packet import pack, unpack, AddChunkPacket,\
    AddChunkReplyPacket


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
