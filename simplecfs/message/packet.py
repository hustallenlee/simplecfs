# -*- coding: utf-8 -*-
"""
define network packet
"""
import json

from simplecfs.common.parameters import *  # NOQA


def pack(data):
    """client pack the data to sending packet and return"""
    return json.dumps(data)


def unpack(packet):
    """ds unpack the data from received packet"""
    return json.loads(packet)


# ---- packet between client and ds ----

class AddChunkPacket(object):
    """
    define the add chunk packet
    """
    def __init__(self, chunk_id, chunk_length):
        """
        @chunk_id: the chunk id to be added
        @chunk_length: chunk data length
        """
        self._message = {}
        self._message['method'] = OP_ADD_CHUNK
        self._message['chunk_id'] = chunk_id
        self._message['length'] = chunk_length

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class AddChunkReplyPacket(object):
    """add chunk reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_ADD_CHUNK_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class DeleteChunkPacket(object):
    """
    define the delete chunk packet
    """
    def __init__(self, chunk_id):
        """
        @chunk_id: the chunk id to be deleted
        """
        self._message = {}
        self._message['method'] = OP_DELETE_CHUNK
        self._message['chunk_id'] = chunk_id

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class DeleteChunkReplyPacket(object):
    """delete chunk reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_DELETE_CHUNK_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class GetChunkPacket(object):
    """
    define the get chunk packet
    """
    def __init__(self, chunk_id, total_blocks, block_list):
        """
        @chunk_id: the chunk id to be get
        @total_blocks: total blocks in one chunk
        @block_list: block num to get(0,1,...,total_blocks-1)
        """
        self._message = {}
        self._message['method'] = OP_GET_CHUNK
        self._message['chunk_id'] = chunk_id
        self._message['total'] = total_blocks
        self._message['list'] = block_list

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class GetChunkReplyPacket(object):
    """get chunk reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_GET_CHUNK_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return get chunk packet message"""
        return self._message


# ---- packet between ds and mds ----

class AddDSPacket(object):
    """
    define the add ds packet
    """
    def __init__(self, rack_id, ds_ip, ds_port):
        """
        @rack_id: rack id of ds
        @ds_ip, @ds_port: ds listen ip and port
        """
        self._message = {}
        self._message['method'] = OP_ADD_DS
        self._message['rack_id'] = rack_id
        self._message['ds_ip'] = ds_ip
        self._message['ds_port'] = ds_port

    def get_message(self):
        """return add ds packet message"""
        return self._message


class AddDSReplyPacket(object):
    """add ds reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_ADD_DS_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return add ds packet message"""
        return self._message


class CheckDSPacket(object):
    """
    define the check ds packet
    """
    def __init__(self):
        self._message = {}
        self._message['method'] = OP_CHECK_DS

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class CheckDSReplyPacket(object):
    """check ds reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_CHECK_DS_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class CheckChunkPacket(object):
    """
    define the check chunk packet
    """
    def __init__(self, chunk_id):
        """
        @chunk_id: the chunk id to be checked
        """
        self._message = {}
        self._message['method'] = OP_CHECK_CHUNK
        self._message['chunk_id'] = chunk_id

    def get_message(self):
        """return add chunk packet message"""
        return self._message


class CheckChunkReplyPacket(object):
    """check chunk reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_CHECK_CHUNK_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return add chunk packet message"""
        return self._message


# ---- packet between client and mds ----

class MakeDirPacket(object):
    """
    define the make dir packet
    """
    def __init__(self, dirname):
        """
        @dirname: dir to be make, absolute path end with '/'
        """
        self._message = {}
        self._message['method'] = OP_MAKE_DIR
        self._message['dirname'] = dirname

    def get_message(self):
        """return make dir packet message"""
        return self._message


class MakeDirReplyPacket(object):
    """make dir reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_MAKE_DIR_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return make dir reply packet message"""
        return self._message


class RemoveDirPacket(object):
    """
    define the remove dir packet
    """
    def __init__(self, dirname):
        """
        @dirname: dir to be removed, absolute path end with '/'
        """
        self._message = {}
        self._message['method'] = OP_REMOVE_DIR
        self._message['dirname'] = dirname

    def get_message(self):
        """return remove dir packet message"""
        return self._message


class RemoveDirReplyPacket(object):
    """remove dir reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_REMOVE_DIR_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return remove dir reply packet message"""
        return self._message


class ListDirPacket(object):
    """
    define the list dir packet
    """
    def __init__(self, dirname):
        """
        @dirname: dir to be listed , absolute path end with '/'
        """
        self._message = {}
        self._message['method'] = OP_LIST_DIR
        self._message['dirname'] = dirname

    def get_message(self):
        """return list dir packet message"""
        return self._message


class ListDirReplyPacket(object):
    """list dir reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        @info: file and directory(endswith '/') list.
        """
        self._message = {}
        self._message['method'] = OP_LIST_DIR_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return list dir reply packet message"""
        return self._message


class StatusDirPacket(object):
    """
    define the status dir packet
    """
    def __init__(self, dirname):
        """
        @dirname: dir to be status, absolute path end with '/'
        """
        self._message = {}
        self._message['method'] = OP_STATUS_DIR
        self._message['dirname'] = dirname

    def get_message(self):
        """return status dir packet message"""
        return self._message


class StatusDirReplyPacket(object):
    """status dir reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        @info: dir info dict.
        """
        self._message = {}
        self._message['method'] = OP_STATUS_DIR_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return status dir reply packet message"""
        return self._message


class ValidDirPacket(object):
    """
    define the valid dir packet
    """
    def __init__(self, dirname):
        """
        @dirname: dir to be valid, absolute path end with '/'
        """
        self._message = {}
        self._message['method'] = OP_VALID_DIR
        self._message['dirname'] = dirname

    def get_message(self):
        """return valid dir packet message"""
        return self._message


class ValidDirReplyPacket(object):
    """valid dir reply packet"""
    def __init__(self, state, info=''):
        """
        @state: RET_FAILURE/RET_SUCCESS/etc.
        """
        self._message = {}
        self._message['method'] = OP_VALID_DIR_REPLY
        self._message['state'] = state
        self._message['info'] = info

    def get_message(self):
        """return valid dir reply packet message"""
        return self._message
