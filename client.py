#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
client shell for simplecfs
"""
import argparse
import ConfigParser as configparser
import cmd
import os

from simplecfs.client.api import Client
from simplecfs.common.parameters import *  # NOQA


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


class Shell(cmd.Cmd):
    """
    client shell
    """
    def cmdloop(self, client, intro=None):
        self.prompt = '(client @ /)-> '
        self.client = client
        return cmd.Cmd.cmdloop(self, intro)

    def do_shell(self, line):
        """
        run some shell command, command startwith '!'
        """
        output = os.popen(line).read()
        print output

    def do_pwd(self):
        """get the current working directory in simplecfs"""
        print self.client.getcwd()

    def do_ls(self, dirname):
        """
        ls [dirctory]
        ls -- list directory contents
        """
        if not dirname:
            dirname = './'

        (state, info) = self.client.listdir(dirname)
        if state == RET_SUCCESS:
            prefix_len = len(self.client.getcwd())
            for i in range(len(info)):
                info[i] = info[i][prefix_len:]
            print '\t'.join(info)
        else:
            print info

    def do_cd(self, dirname):
        """
        cd [dirctory]
        cd -- change working directory
        """
        if not dirname:
            dirname = '/'
        (state, info) = self.client.chdir(dirname)
        if state == RET_SUCCESS:
            self.prompt = '(client @ %s)-> ' % self.client.getcwd()
        else:
            print info

    def do_mkdir(self, dirname):
        """
        mkdir dirctory
        mkdir -- make a directory
        """
        if not dirname:
            print 'try help mkdir'
            return

        (state, info) = self.client.mkdir(dirname)
        if state != RET_SUCCESS:
            print info

    def do_rmdir(self, dirname):
        """
        rmdir dirctory
        rmdir -- remove directory
        """
        if not dirname:
            print 'try help rmdir'
            return

        (state, info) = self.client.rmdir(dirname)
        if state != RET_SUCCESS:
            print info

    def do_put(self, args):  # NOQA
        """
        put src dst [rs|crs|z] [k] [m] [packet_size] [block_size] [w]
        put @src to @dst with code info
        example: put ~/test.txt /test.txt rs 2 2 1024 1024 8
        """
        args = args.split()
        src_path = ''
        dst_path = ''
        code_info = {
            'type': CODE_RS,
            'k': 2,
            'm': 2,
            'packet_size': 512,
            'block_size': 1024,
            'w': 8,
        }
        argc = len(args)
        if argc < 3:
            print 'try help put'
            return

        src_path = args[0]
        dst_path = args[1]
        if args[2] == 'rs':
            code_info['type'] = CODE_RS
        elif args[2] == 'crs':
            code_info['type'] = CODE_CRS
        elif args[2] == 'z':
            code_info['type'] = CODE_Z
        else:
            print 'args[2]: %s' % args[2]
            print 'parameters error, try help put'
            return

        if argc > 3:
            code_info['k'] = int(args[3])
        if argc > 4:
            code_info['m'] = int(args[4])
        if argc > 5:
            code_info['packet_size'] = int(args[5])
        if argc > 6:
            code_info['block_size'] = int(args[6])
        if argc > 7:
            code_info['w'] = int(args[7])

        (state, info) = self.client.putfile(src_path, dst_path, code_info)
        if state == RET_SUCCESS:
            print 'put successful'
        else:
            print info

    def do_stat(self, path):
        """
        stat   path
        statfile -- display file or directory(endswith '/') status
        """
        if not path:
            print 'try help stat'
            return

        if path.endswith('/'):
            (state, info) = self.client.statdir(path)
        else:
            (state, info) = self.client.statfile(path)
        print info

    def do_get(self, args):
        """
        get src local
        get -- get file from @src to @lcoal
        """
        args = args.split()
        src_path = ''
        local_path = ''
        argc = len(args)
        if argc < 2:
            print 'try help get'
            return

        src_path = args[0]
        local_path = args[1]

        (state, info) = self.client.getfile(src_path, local_path)
        if state == RET_SUCCESS:
            print 'get successful'
        else:
            print info

    def do_rm(self, filename):
        """
        rm filename
        rm -- remove file
        """
        if not filename:
            print 'try help rm'
            return

        (state, info) = self.client.delfile(filename)
        if state != RET_SUCCESS:
            print info

    def do_exit(self, args):
        """
        exit shell
        """
        return True

    def do_EOF(self, args):
        """
        exit shell (ctrl+d)
        """
        return True

    def emptyline(self):
        return cmd.Cmd.emptyline(self)


if __name__ == '__main__':
    client = init()
    Shell().cmdloop(client, intro='Welcome to simplecfs shell!\n'+'-'*50)
