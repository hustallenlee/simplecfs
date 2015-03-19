# -*- coding: utf-8 -*-
'''
handle meta data storage: set, get, delete, exists of meta data
'''
import redis
import logging
import json

from simplecfs.mds.meta_table import dir_key, sub_key, ds_key, ds_alive_key,\
    tmp_key, file_key, obj_key, chk_key
from simplecfs.common.parameters import DS_BROKEN, RET_SUCCESS


class MDSStore(object):
    '''class to handle meta data operation'''
    def __init__(self, host='127.0.0.1', port=6379, db=0, expire_time=1800):
        '''init storage'''
        try:
            self.r = redis.StrictRedis(host, port, db)
        except redis.exceptions.ConnectionError:
            logging.exception('redis connect error')

        # init root
        if not self.hasdir('/'):
            self.set(dir_key('/'), '')  # add root directory

        self.expire_time = expire_time

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
        return ret

    def expire(self, key, timeout):
        '''expire a key for timeout'''
        ret = self.r.expire(key, timeout)
        return ret

    # directory operations

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

    # ds operations

    def add_alive_ds(self, ds_ip, ds_port):
        key = ds_alive_key()
        item = '%s:%d' % (ds_ip, ds_port)
        lists = self.get(key)
        if not lists:
            lists = []

        ret = True
        if item not in lists:
            lists.append(item)
            ret = self.set(key, lists)

        return ret

    def del_alive_ds(self, ds_ip, ds_port):
        key = ds_alive_key()
        item = '%s:%d' % (ds_ip, ds_port)
        lists = self.get(key)

        ret = True
        if item in lists:
            lists.remove(item)
            ret = self.set(key, lists)

        return ret

    def get_alive_ds(self):
        key = ds_alive_key()
        lists = self.get(key)

        return lists

    def is_alive_ds(self, ds_ip, ds_port):
        key = ds_alive_key()
        item = '%s:%d' % (ds_ip, ds_port)
        lists = self.get(key)

        ret = False
        if item in lists:
            ret = True

        return ret

    def addds(self, ds_ip, ds_port, dsinfo):
        logging.info('meta addds ip:%s,port:%s,info:%s', ds_ip, ds_port, dsinfo)

        key = ds_key(ds_ip, ds_port)
        ret = self.set(key, dsinfo)

        if ret == RET_SUCCESS:
            ret = self.add_alive_ds(ds_ip, ds_port)

        return ret

    def updateds(self, ds_ip, ds_port, dsinfo):
        logging.info('updateds ip:%s,port:%s,info:%s', ds_ip, ds_port, dsinfo)

        key = ds_key(ds_ip, ds_port)
        ret = self.set(key, dsinfo)

        if ret and dsinfo['status'] == DS_BROKEN:
            ret = self.del_alive_ds(ds_ip, ds_port)

        return ret

    def hasds(self, ds_ip, ds_port):
        logging.info('meta hasds: ip:%s port:%d', ds_ip, ds_port)
        return self.exists(ds_key(ds_ip, ds_port))

    def delds(self, ds_ip, ds_port):
        logging.info('meta delds: ip:%s port:%d', ds_ip, ds_port)
        key = ds_key(ds_ip, ds_port)
        ret = self.delete(key)

        if ret == RET_SUCCESS:
            ret = self.del_alive_ds(ds_ip, ds_port)

        return ret

    def getds(self, ds_ip, ds_port):
        logging.info('meta getds: ip:%s port:%d', ds_ip, ds_port)
        key = ds_key(ds_ip, ds_port)
        return self.get(key)

    # tmp file operations

    def addtmp(self, filename, fileinfo):
        logging.info('meta addtmp filename %s', filename)

        key = tmp_key(filename)
        ret = self.set(key, fileinfo)

        if ret == RET_SUCCESS:
            ret = self.expire(key, self.expire_time)

        return ret

    def hastmp(self, filename):
        logging.info('meta hastmp: file %s', filename)
        return self.exists(tmp_key(filename))

    def deltmp(self, filename):
        logging.info('meta deltmp: file %s', filename)
        key = tmp_key(filename)
        self.delete(key)

        return True

    def gettmp(self, filename):
        logging.info('meta gettmp: file %s', filename)
        key = tmp_key(filename)
        return self.get(key)

    def addfile(self, filename, fileinfo):
        logging.info('meta addfile filename %s', filename)

        key = file_key(filename)
        ret = self.set(key, fileinfo)
        return ret

    def hasfile(self, filename):
        logging.info('meta hasfile: file %s', filename)
        return self.exists(file_key(filename))

    def delfile(self, filename):
        logging.info('meta delfile: file %s', filename)
        key = file_key(filename)
        self.delete(key)

        return True

    def getfile(self, filename):
        logging.info('meta getfile: file %s', filename)
        key = file_key(filename)
        return self.get(key)

    def addobj(self, objname, objinfo):
        logging.info('meta addobj objname %s', objname)

        key = obj_key(objname)
        ret = self.set(key, objinfo)
        return ret

    def hasobj(self, objname):
        logging.info('meta hasobj: obj %s', objname)
        return self.exists(obj_key(objname))

    def delobj(self, objname):
        logging.info('meta delobj: obj %s', objname)
        key = obj_key(objname)
        self.delete(key)

        return True

    def getobj(self, objname):
        logging.info('meta getobj: obj %s', objname)
        key = obj_key(objname)
        return self.get(key)

    def addchk(self, chkname, chkinfo):
        logging.info('meta addchk chkname %s', chkname)

        key = chk_key(chkname)
        ret = self.set(key, chkinfo)
        return ret

    def haschk(self, chkname):
        logging.info('meta haschk: chk %s', chkname)
        return self.exists(chk_key(chkname))

    def delchk(self, chkname):
        logging.info('meta delchk: chk %s', chkname)
        key = chk_key(chkname)
        self.delete(key)

        return True

    def getchk(self, chkname):
        logging.info('meta getchk: chk %s', chkname)
        key = chk_key(chkname)
        return self.get(key)
