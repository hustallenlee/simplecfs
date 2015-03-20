#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use Client for test
"""
import argparse
import ConfigParser as configparser

from simplecfs.client.api import Client


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
    print 'current directory: '
    print client.getcwd()
