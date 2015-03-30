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

des_path = './64M.txt'
base_path = '/home/qing/simplecfs/storage/'
src_path = ''

code_info = {  # default code info
    'type': CODE_RS,
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
    client = Client(config, test=True)
    return client


def test_putfile(client):
    client.putfile(src_path, des_path, code_info)


def test_normal_get_chunk(client):
    chunk_id = '/64M.txt_obj0_chk0'
    local_path = '/home/qing/simplecfs/storage/rschk0'
    client.getchunk(chunk_id, local_path)

def test_degrade_get_chunk(client):
    chunk_id = '/64M.txt_obj0_chk0'
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    client.report_ds(ip, port, DS_BROKEN)
    degrade_path = '/home/qing/simplecfs/storage/degrade_rschk0'
    client.getchunk(chunk_id, degrade_path)
    client.report_ds(ip, port, DS_CONNECTED)

def test_delete_file(client):
    des_path = './64M.txt'
    client.delfile(des_path)

if __name__ == '__main__':
    client = init()
    size_num = [1,2,4,8,16,32,64,128,256,512]
    size_num = [512]
    for each_num in size_num:
        file_name = str(each_num)+'M.txt'
        src_path = base_path+file_name
        file_size = each_num*(1024*1024)
        code_info['block_size'] = (file_size/(3*1024)+1)*1024
        total_time = 0
        for i in xrange(10):
            t1 = time.time()
            test_putfile(client)
            total_time += time.time()-t1
            test_delete_file(client)
        print  file_name[:-4], total_time/10,
            
            
        file_name = str(each_num)+'Mdeg.txt'
        src_path = base_path+file_name
        code_info['block_size'] = file_size
        test_putfile(client)
        total_time = 0
        for i in xrange(10):
            t1 = time.time()
            test_degrade_get_chunk(client)
            total_time += time.time()-t1
        print total_time/10
        test_delete_file(client)
    # # ---- test rs code ----
    # test_putfile(client)

    # test_normal_get_chunk(client)

    # test_degrade_get_chunk(client)

    #test_delete_file(client)
