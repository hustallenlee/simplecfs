#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
unit test for ds
"""
import ConfigParser as configparser
import logging
import logging.handlers

import eventlet
from nose.tools import eq_

from simplecfs.ds.server import DSServer
from simplecfs.message.packet import AddChunkPacket, DeleteChunkPacket,\
    GetChunkPacket
from simplecfs.message.network_handler import send_command, recv_command,\
    send_data, recv_data
from simplecfs.common.parameters import OP_ADD_CHUNK_REPLY, OP_DELETE_CHUNK_REPLY,\
    OP_GET_CHUNK_REPLY, RET_SUCCESS

DATA_FILE = './test.bak'
DATA_LENGTH = 6660000
DS_CONFIG_FILE = './conf/ds.cfg'
CLIENT_CONFIG_FILE = './conf/client.cfg'
POOL = eventlet.GreenPool(10)


def start_server(ds_):
    print 'start server'
    ds_.start()


def get_new_connection():
    # get config options
    config = configparser.ConfigParser()
    config.read(CLIENT_CONFIG_FILE)
    ds_ip = config.get('dataserver', 'ds_ip')
    ds_port = config.getint('dataserver', 'ds_port')
    print 'connect to server'
    return eventlet.connect((ds_ip, ds_port))


def test_ds():
    """test function: add_chunk(chunk_id, chunk_length, chunk_data)"""
    # start the sever to receive command
    # get config options
    config = configparser.ConfigParser()
    config.read(DS_CONFIG_FILE)

    # start server
    ds_ = DSServer(config)
    POOL.spawn_n(start_server, ds_)

    # test add chunk
    chunk_id = 'obj0_chk0'
    length = DATA_LENGTH
    data = open(DATA_FILE, 'rb').read(length)

    packet = AddChunkPacket(chunk_id, length)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    # sending data
    send_data(sock_fd, data)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    sock_fd.close()
    eq_(recv['state'], RET_SUCCESS)
    eq_(recv['method'], OP_ADD_CHUNK_REPLY)

    # test get chunk
    """test function: get_chunk(chunk_id, total_blocks, block_list)"""
    chunk_id = 'obj0_chk0'
    total_blocks = 10
    block_list = [0, 1, 2, 3, 4]

    packet = GetChunkPacket(chunk_id, total_blocks, block_list)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile('rw')

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    eq_(recv['state'], RET_SUCCESS)
    eq_(recv['method'], OP_GET_CHUNK_REPLY)

    # recieve data
    get_data = recv_data(sock_fd)
    eq_(get_data, data[:length/2])

    # test delete chunk
    """test function: delete_chunk(chunk_id)"""
    chunk_id = 'obj0_chk0'

    packet = DeleteChunkPacket(chunk_id)
    msg = packet.get_message()

    sock = get_new_connection()
    sock_fd = sock.makefile()

    logging.info('%s', msg)
    send_command(sock_fd, msg)

    recv = recv_command(sock_fd)
    print recv
    logging.info('recv: %s', recv)
    eq_(recv['state'], RET_SUCCESS)
    eq_(recv['method'], OP_DELETE_CHUNK_REPLY)


def test_check_ds():
    """test function: check_ds()"""
    pass


def test_check_chunk():
    """test function: check_chunk(chunk_id)"""
    pass
