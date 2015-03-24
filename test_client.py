#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use Client for test
"""
import argparse
import ConfigParser as configparser

from simplecfs.client.api import Client
# from simplecfs.common.parameters import CODE_RS


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
    # des_path = './test.txt'
    # src_path = '/Users/lijian/temp/test/test.txt'
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
    # print 'delfile:'
    # print client.delfile(des_path)
