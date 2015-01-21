#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
start the client for test
"""
import argparse
import ConfigParser as configparser
import logging
import logging.handlers

import eventlet

from simplecfs.message.packet import AddChunkPacket, DeleteChunkPacket
from simplecfs.message.network_handler import send_command, recv_command,\
    send_data

FRAME_SIZE = 1024
DATA_FILE = './test.bak'
DATA_LENGTH = 66614904


def get_new_connection(ip_='127.0.0.1', port=7000):
    return eventlet.connect((ip_, port))


def test_add_chunk():
    """test function: add_chunk(chunk_id, chunk_length, chunk_data)"""
    chunk_id = 'obj0_chk0'
    length = DATA_LENGTH
    data = open(DATA_FILE, 'rb').read()

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


def test_delete_chunk():
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


def test_get_chunk():
    """test function: get_chunk(chunk_id, total_blocks, block_list)"""
    pass


def test_check_ds():
    """test function: check_ds()"""
    pass


def test_check_chunk():
    """test function: check_chunk(chunk_id)"""
    pass


def main():
    """run the dataserver main function"""
    # handle command line argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        metavar='CONFIG_FILE',
                        help='clientconfig file',
                        default='./conf/client.cfg')
    args = parser.parse_args()
    config_file = args.config

    # get config options
    config = configparser.ConfigParser()
    config.read(config_file)

    # init logging
    logger = logging.getLogger()  # get the 'root' logger
    level = getattr(logging, config.get('log', 'log_level'))
    logger.setLevel(level)
    log_name = config.get('log', 'log_name')
    log_max_bytes = config.getint('log', 'log_max_bytes')
    log_file_num = config.getint('log', 'log_file_num')
    handler = logging.handlers.RotatingFileHandler(log_name,
                                                   maxBytes=log_max_bytes,
                                                   backupCount=log_file_num)
    log_format = logging.Formatter('%(levelname)-8s[%(asctime)s.%(msecs)d]'
                                   '<%(module)s> %(funcName)s:%(lineno)d:'
                                   ' %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(log_format)
    logger.addHandler(handler)

    # start client test
    test_add_chunk()
    test_delete_chunk()

if __name__ == '__main__':
    main()
