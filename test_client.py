#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use Client for test
"""
import argparse
import ConfigParser as configparser

from simplecfs.client.api import Client
from simplecfs.common.parameters import CODE_RS, CODE_CRS, CODE_Z  # NOQA
from simplecfs.common.parameters import DS_BROKEN, DS_CONNECTED  # NOQA


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


if __name__ == '__main__':
    client = init()
    # print 'current directory: '
    # print client.getcwd()
    # dirname = '/testdir/'
    # print client.mkdir(dirname)
    # print client.listdir('/')
    # print client.listdir(dirname)
    # print client.statdir('nosuchdir/')
    # print client.statdir(dirname)
    # print client.chdir(dirname)
    # print client.getcwd()
    # print client.rmdir(dirname)
    # print client.chdir('/')
    # print client.getcwd()
    # print client.rmdir(dirname)
    # print client.statdir(dirname)
    # print client.chdir(dirname)
    # print client.getcwd()

    # ip = '127.0.0.1'
    # port = 7001
    # print 'change ds to ds broken'
    # print client.report_ds(ip, port, DS_BROKEN)
    # print 'change ds to ds connected'
    # print client.report_ds(ip, port, DS_CONNECTED)

    # # ---- test rs code ----
    # des_path = './rstest.txt'
    # src_path = '/Users/lijian/temp/test/rstest.txt'
    # code_info = {  # default code info
    #     'type': CODE_RS,
    #     'k': 2,
    #     'm': 2,
    #     'w': 8,
    #     'packet_size': 512,
    #     'block_size': 1024,
    # }
    # print 'putfile: '
    # print client.putfile(src_path, des_path, code_info)
    # print 'statfile: '
    # print client.statfile(des_path)

    # chunk_id = '/rstest.txt_obj0_chk0'
    # local_path = '/Users/lijian/temp/test/rschk0'
    # print 'normal read chunk'
    # print client.getchunk(chunk_id, local_path)

    # print 'get chunk ds_id:'
    # (ip, port) = client.get_chunk_ds_id(chunk_id)
    # print 'report ds:'
    # print client.report_ds(ip, port, DS_BROKEN)
    # print 'degrade read chunk'
    # degrade_path = '/Users/lijian/temp/test/degrade_rschk0'
    # print client.getchunk(chunk_id, degrade_path)
    # print 'report ds:'
    # print client.report_ds(ip, port, DS_CONNECTED)

    # print 'get object test'
    # object_id = '/rstest.txt_obj0'
    # local_path = '/Users/lijian/temp/test/rsobj0'
    # print 'get object: '
    # print client.getobject(object_id, local_path)

    # print 'get file test:'
    # des_path = '/rstest.txt'
    # local_path = '/Users/lijian/temp/test/rstestget.txt'
    # print client.getfile(des_path, local_path)

    # print 'delfile:'
    # print client.delfile(des_path)

    # # ---- test crs code ----
    # des_path = './crstest.txt'
    # src_path = '/Users/lijian/temp/test/crstest.txt'
    # code_info = {
    #     'type': CODE_CRS,
    #     'k': 2,
    #     'm': 2,
    #     'w': 8,
    #     'packet_size': 512,
    #     'block_size': 1024,
    # }
    # print 'putfile: '
    # print client.putfile(src_path, des_path, code_info)
    # print 'statfile: '
    # print client.statfile(des_path)

    # chunk_id = '/crstest.txt_obj0_chk0'
    # local_path = '/Users/lijian/temp/test/crschk0'
    # print 'normal read chunk'
    # print client.getchunk(chunk_id, local_path)

    # print 'get chunk ds_id:'
    # (ip, port) = client.get_chunk_ds_id(chunk_id)
    # print 'report ds:'
    # print client.report_ds(ip, port, DS_BROKEN)
    # print 'degrade read chunk'
    # degrade_path = '/Users/lijian/temp/test/degrade_crschk0'
    # print client.getchunk(chunk_id, degrade_path)
    # print 'report ds:'
    # print client.report_ds(ip, port, DS_CONNECTED)
    # print 'delfile:'
    # print client.delfile(des_path)

    # print 'get object test'
    # object_id = '/crstest.txt_obj0'
    # local_path = '/Users/lijian/temp/test/crsobj0'
    # print 'get object: '
    # print client.getobject(object_id, local_path)

    # print 'get file test:'
    # des_path = '/crstest.txt'
    # local_path = '/Users/lijian/temp/test/crstestget.txt'
    # print client.getfile(des_path, local_path)

    # # ---- test zcode ----
    # des_path = './ztest.txt'
    # src_path = '/Users/lijian/temp/test/ztest.txt'
    # code_info = {
    #     'type': CODE_Z,
    #     'k': 2,
    #     'm': 2,
    #     'packet_size': 512,
    #     'block_size': 1024,
    # }
    # print 'putfile: '
    # print client.putfile(src_path, des_path, code_info)
    # print 'statfile: '
    # print client.statfile(des_path)

    # chunk_id = '/ztest.txt_obj0_chk0'
    # local_path = '/Users/lijian/temp/test/zchk0'
    # print 'normal read chunk'
    # print client.getchunk(chunk_id, local_path)

    # print 'get chunk ds_id:'
    # (ip, port) = client.get_chunk_ds_id(chunk_id)
    # print 'report ds:'
    # print client.report_ds(ip, port, DS_BROKEN)
    # print 'degrade read chunk'
    # degrade_path = '/Users/lijian/temp/test/degrade_zchk0'
    # print client.getchunk(chunk_id, degrade_path)
    # print 'report ds:'
    # print client.report_ds(ip, port, DS_CONNECTED)
    # print 'delfile:'
    # print client.delfile(des_path)

    # print 'get object test'
    # object_id = '/ztest.txt_obj0'
    # local_path = '/Users/lijian/temp/test/zobj0'
    # print 'get object: '
    # print client.getobject(object_id, local_path)

    # print 'get file test:'
    # des_path = '/ztest.txt'
    # local_path = '/Users/lijian/temp/test/ztestget.txt'
    # print client.getfile(des_path, local_path)
