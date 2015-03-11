# -*- coding: utf-8 -*-
'''
handle meta data storage: set, get, delete, exists of meta data
'''
import redis
import logging
import json

from simplecfs.mds.meta_table import dir_key, sub_key, ds_key


class MDSStore(object):
    '''class to handle meta data operation'''
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        '''init storage'''
        try:
            self.r = redis.StrictRedis(host, port, db)
        except redis.exceptions.ConnectionError:
            logging.exception('redis connect error')

        # init root
        if not self.hasdir('/'):
            self.set(dir_key('/'), '')  # add root directory

    def set(self, key, value):
        '''set data'''
        ret = self.r.set(key, json.dumps(value))
        return ret

    def get(self, key):
        '''get data by key'''
        ret = self.r.get(key)
        if not ret:
            return ''
        return json.loads(ret)

    def delete(self, key):
        '''delete data by key'''
        ret = self.r.delete(key)
        return bool(ret)

    def exists(self, key):
        '''exists a key'''
        ret = self.r.exists(key)
        return bool(ret)

    def mkdir(self, dirname, dirinfo):
        logging.info('meta mkdir %s, %s', dirname, dirinfo)
        if dirname == '/':
            return False

        parent = ''.join(dirname[:-1].rpartition('/')[0:2])  # get the parent
        ret = self.addsub(parent, dirname)

        if ret:
            ret = self.set(dir_key(dirname), dirinfo)

        return ret

    def hasdir(self, dirname):
        logging.info('meta hasdir %s', dirname)
        return self.exists(dir_key(dirname))

    def statdir(self, dirname):
        logging.info('meta statdir: %s', dirname)
        return self.get(dir_key(dirname))

    def deldir(self, dirname):
        logging.info('meta deldir: %s', dirname)
        if dirname == '/':
            return False

        parent = ''.join(dirname[:-1].rpartition('/')[0:2])  # get the parent
        ret = self.delsub(parent, dirname)

        if ret:
            ret = self.delete(dir_key(dirname))

        return ret

    def lsdir(self, dirname):
        logging.info('meta lsdir: %s', dirname)
        return self.get(sub_key(dirname))

    def addsub(self, parent, subfile):
        logging.info('meta addsub parent:%s, sub: %s', parent, subfile)
        key = sub_key(parent)
        subs = self.get(key)
        if not subs:  # None
            subs = []

        if subfile in subs:
            return True

        subs.append(subfile)
        ret = self.set(key, subs)
        return ret

    def delsub(self, parent, subfile):
        logging.info('meta delsub parent:%s, sub: %s', parent, subfile)
        key = sub_key(parent)
        subs = self.get(key)
        if not subs:  # None
            subs = []

        if subfile not in subs:
            return True

        subs.remove(subfile)
        if subs:
            ret = self.set(key, subs)
        else:
            ret = self.delete(key)
        return ret

    def hassub(self, dirname):
        logging.info('meta hassub %s', dirname)
        return self.exists(sub_key(dirname))

    def addds(self, ds_ip, ds_port, dsinfo):
        logging.info('meta addds ip:%s,port:%s,info:%s', ds_ip, ds_port, dsinfo)

        key = ds_key(ds_ip, ds_port)
        ret = self.set(key, dsinfo)
        return ret

    def updateds(self, ds_ip, ds_port, dsinfo):
        logging.info('updateds ip:%s,port:%s,info:%s', ds_ip, ds_port, dsinfo)

        key = ds_key(ds_ip, ds_port)
        ret = self.set(key, dsinfo)
        return ret

    def hasds(self, ds_ip, ds_port):
        logging.info('meta hasds: ip:%s port:%d', ds_ip, ds_port)
        return self.exists(ds_key(ds_ip, ds_port))

    def delds(self, ds_ip, ds_port):
        logging.info('meta delds: ip:%s port:%d', ds_ip, ds_port)
        key = ds_key(ds_ip, ds_port)
        return self.delete(key)

    def getds(self, ds_ip, ds_port):
        logging.info('meta getds: ip:%s port:%d', ds_ip, ds_port)
        key = ds_key(ds_ip, ds_port)
        return self.get(key)
