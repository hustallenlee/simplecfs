#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use Client for test
"""
import argparse
import ConfigParser as configparser
import time

from simplecfs.client.api import Client
from simplecfs.common.parameters import CODE_Z
from simplecfs.common.parameters import DS_BROKEN, DS_CONNECTED

des_path = './testM.txt'
base_path = '/Users/lijian/temp/test/'
src_path = ''

code_info = {  # default code info
    'type': CODE_Z,
    'k': 3,
    'm': 2,
    'w': 8,
    'packet_size': 1024,
    'block_size': 33554432,  # 32M
}


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
    local_path = base_path + 'zchk0'
    t1 = time.time()
    client.getchunk(chunk_id, local_path)
    interval = time.time()-t1
    return interval * 1000  # ms


def test_degrade_get_chunk(client):
    chunk_id = '/testM.txt_obj0_chk0'
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    client.report_ds(ip, port, DS_BROKEN)
    degrade_path = base_path + 'degrade_zchk0'

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
    # size_num = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    size_num = [1, 2]  # test 1M, 2M file
    print 'zcode:'
    print '%s %s %s %s' % ('filesize', 'putfile(ms)',
                           'getchunk(ms)', 'get_degraded_chunk(ms)')
    for each_num in size_num:
        file_name = str(each_num)+'M.txt'
        src_path = base_path+file_name
        file_size = each_num*(1024*1024)
        r = 4
        code_info['block_size'] = (file_size/(3*4*1024)+1)*1024
        total_time = 0
        for i in xrange(10):
            total_time += test_putfile(client)
            test_delete_file(client)
        print file_name[:-4], total_time/10,

        file_name = str(each_num)+'Mdeg.txt'
        src_path = base_path+file_name
        code_info['block_size'] = file_size/r
        test_putfile(client)
        total_time = 0
        for i in xrange(10):
            total_time += test_normal_get_chunk(client)
        print total_time/10,

        total_time = 0
        for i in xrange(10):
            total_time += test_degrade_get_chunk(client)
        print total_time/10
        test_delete_file(client)
