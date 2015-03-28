#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use Client for test
"""
import argparse
import ConfigParser as configparser

from simplecfs.client.api import Client
from simplecfs.common.parameters import CODE_RS
from simplecfs.common.parameters import DS_BROKEN, DS_CONNECTED


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
    des_path = './64M.txt'
    src_path = '/home/f309/simplecfs/storage/64M.txt'
    code_info = {  # default code info
        'type': CODE_RS,
        'k': 2,
        'm': 2,
        'w': 8,
        'packet_size': 1024,
        'block_size': 33554432,  # 32M
    }
    print 'putfile: '
    print client.putfile(src_path, des_path, code_info)
    print 'statfile: '
    print client.statfile(des_path)


def test_normal_get_chunk(client):
    chunk_id = '/64M.txt_obj0_chk0'
    local_path = '/home/f309/simplecfs/storage/rschk0'
    print 'normal read chunk'
    print client.getchunk(chunk_id, local_path)

def test_degrade_get_chunk(client):
    chunk_id = '/64M.txt_obj0_chk0'
    print 'get chunk ds_id:'
    (ip, port) = client.get_chunk_ds_id(chunk_id)
    print 'report ds:'
    print client.report_ds(ip, port, DS_BROKEN)
    print 'degrade read chunk'
    degrade_path = '/home/f309/simplecfs/storage/degrade_rschk0'
    print client.getchunk(chunk_id, degrade_path)
    print 'report ds:'
    print client.report_ds(ip, port, DS_CONNECTED)

def test_delete_file(client):
    des_path = './64M.txt'
    print 'delfile:'
    print client.delfile(des_path)

if __name__ == '__main__':
    client = init()
    # # ---- test rs code ----
    # test_putfile(client)

    # test_normal_get_chunk(client)

    # test_degrade_get_chunk(client)

    # test_delete_file(client)
