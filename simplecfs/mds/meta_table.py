# -*- coding: utf-8 -*-
"""
define meta data table names prefix
"""
# table prefix
DIR_PREFIX = 'dir:'     # directory
SUB_PREFIX = 'sub:'     # subfiles
FILE_PREFIX = 'file:'   # file
OBJ_PREFIX = 'obj:'     # object
CHK_PREFIX = 'chk:'     # chunk
DS_PREFIX = 'ds:'       # ds
DS_ALIVE = 'ds_alive'   # ds alive list


def dir_key(dirname):
    """use dirname to get dir key"""
    return DIR_PREFIX + dirname


def sub_key(dirname):
    """use dirname to get subfiles key"""
    return SUB_PREFIX + dirname


def file_key(filename):
    """use filename to get file key"""
    return FILE_PREFIX + filename


def obj_key(objname):
    """use object name to get object key"""
    return OBJ_PREFIX + objname


def chk_key(chkname):
    """use chunk name to get chunk key"""
    return CHK_PREFIX + chkname


def ds_key(ip, port):
    """use ip and port to get ds key"""
    return DS_PREFIX + ip + ':' + str(port)


def ds_alive_key():
    return DS_ALIVE
