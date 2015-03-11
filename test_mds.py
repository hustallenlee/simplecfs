#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
start the client for test mds
"""
import argparse
import ConfigParser as configparser
import logging
import logging.handlers

import eventlet

from simplecfs.message.packet import MakeDirPacket, RemoveDirPacket,\
    ListDirPacket, StatusDirPacket, ValidDirPacket, AddDSPacket,\
    ReportDSPacket
from simplecfs.message.network_handler import send_command, recv_command


def get_new_connection(ip_='127.0.0.1', port=8000):
    return eventlet.connect((ip_, port))


def test_make_dir(dirname='/testdir/'):
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


def test_remove_dir(dirname='/testdir/'):
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


def test_list_dir(dirname='/'):
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


def test_status_dir(dirname='/testdir/'):
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


def test_valid_dir(dirname='/testdir/'):
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


def test_add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7000):
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


def test_report_ds():
    """test function: report_ds(info)
    report ds state info to mds
    """
    ds_ip = '127.0.0.1'
    ds_port = 7000
    info = {
        'space': 102400,
        'chunk_num': 898,
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


def main():
    """init client"""
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

    # start test mds
    dirname = '/testdir/'
    test_make_dir(dirname)
    test_list_dir('/')
    test_list_dir(dirname)
    test_status_dir(dirname)
    test_status_dir('/nosuchdir/')
    test_valid_dir(dirname)
    test_valid_dir('/nosuchdir/')
    test_remove_dir('/nosuchdir/')
    test_remove_dir(dirname)
    test_list_dir('/')
    test_status_dir(dirname)
    test_valid_dir(dirname)

    test_add_ds(rack_id=0, ds_ip='127.0.0.1', ds_port=7000)
    test_report_ds()


if __name__ == '__main__':
    main()