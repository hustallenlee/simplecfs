#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use Client for test
"""
import argparse
import ConfigParser as configparser
import time

from simplecfs.client.api import Client
from simplecfs.common.parameters import CODE_RS
from simplecfs.common.parameters import DS_BROKEN, DS_CONNECTED

des_path = './testM.txt'
base_path = '/Users/lijian/temp/test/'
src_path = ''
file_name = '64M.txt'
file_size = 64  # M

code_info = {  # default code info
    'type': CODE_RS,
    'k': 3,
    'm': 2,
    'w': 8,
    'packet_size': 1024,
    'block_size': 33554432,  # 32M
}


def get_block_size(file_size, k):
    if file_size % (k*256) == 0:
        return file_size/k
    return (file_size/(k*256)+1)*256


def init():
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

    # get the client
    client = Client(config)
    return client


def test_putfile(client):
    t1 = time.time()
    client.putfile(src_path, des_path, code_info)
    interval = time.time()-t1
    return interval * 1000  # ms


def test_normal_get_chunk(client):
    chunk_id = '/testM.txt_obj0_chk0'
    local_path = base_path + 'rschk0'
    t1 = time.time()
    client.getchunk(chunk_id, local_path)
    interval = time.time()-t1
    return interval * 1000  # ms


def test_degrade_get_chunk(client):
    chunk_id = '/testM.txt_obj0_chk0'
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    client.report_ds(ip, port, DS_BROKEN)
    degrade_path = base_path + 'degrade_rschk0'

    t1 = time.time()
    client.getchunk(chunk_id, degrade_path)
    interval = time.time()-t1
    client.report_ds(ip, port, DS_CONNECTED)

    return interval * 1000  # ms


def test_delete_file(client):
    des_path = './testM.txt'
    client.delfile(des_path)


if __name__ == '__main__':
    client = init()
    # (m, k)
    params = [(2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9),
              (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8),
              (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7)]
    params = [(2, 2), (2, 3)]
    print 'rs:'
    print '%s %s %s %s' % ('(m, k)', 'putfile(ms)',
                           'getchunk(ms)', 'degraded_chunk(ms)')
    for each_num in params:
        print each_num
        m = each_num[0]
        k = each_num[1]
        code_info['k'] = k
        code_info['m'] = m
        print '(%d,%d), ' % (m, k)
        src_path = base_path+file_name
        # code_info['block_size'] = (file_size*1024*1024/(k*1024)+1)*1024
        code_info['block_size'] = get_block_size(file_size*1024*1024, k)
        total_time = 0
        for i in xrange(5):
            total_time += test_putfile(client)
            test_delete_file(client)
        print total_time/5,

        file_name = str(k*file_size)+'M.txt'
        print 'read filename: %s' % file_name
        src_path = base_path+file_name
        code_info['block_size'] = file_size*1024*1024
        test_putfile(client)
        total_time = 0
        for i in xrange(5):
            total_time += test_normal_get_chunk(client)
        print total_time/5,

        total_time = 0
        for i in xrange(5):
            total_time += test_degrade_get_chunk(client)
        print total_time/5
        test_delete_file(client)
