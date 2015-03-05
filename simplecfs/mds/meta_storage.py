# -*- coding: utf-8 -*-
"""
handle meta data storage: set, get, delete, exists of meta data
"""
import redis
import logging
import json


class MDSStore(object):
    """class to handle meta data operation"""
    def __init__(self, host='127.0.0.1', port=6379, db=0):
        """init storage"""
        try:
            self.r = redis.StrictRedis(host, port, db)
        except redis.exceptions.ConnectionError:
            logging.exception("redis connect error")

    def set(self, key, value):
        """set data"""
        ret = self.r.set(key, json.dumps(value))
        return ret

    def get(self, key):
        """get data by key"""
        ret = self.r.get(key)
        return json.loads(ret)

    def delete(self, key):
        """delete data by key"""
        ret = self.r.delete(key)
        return ret

    def exists(self, key):
        """exists a key"""
        ret = self.r.exists(key)
        return ret
