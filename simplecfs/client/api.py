# -*- coding: utf-8 -*-
"""
client api
"""
import logging
import logging.handlers
import eventlet
from os.path import normpath, getsize

from simplecfs.message.packet import MakeDirPacket, ListDirPacket,\
    ValidDirPacket, StatusDirPacket, RemoveDirPacket, AddFilePacket,\
    AddChunkPacket, AddFileCommitPacket, StatFilePacket, DeleteFilePacket,\
    DeleteChunkPacket, GetChkPacket, GetChunkPacket, ReportDSPacket,\
    GetObjPacket
from simplecfs.coder.driver import RSDriver, CRSDriver, ZDriver
from simplecfs.message.network_handler import send_command, recv_command,\
    send_data, recv_data
from simplecfs.common.parameters import RET_FAILURE, RET_SUCCESS, CODE_RS,\
    CODE_CRS, CODE_Z, CHUNK_OK, CHUNK_MISSING, DS_CONNECTED


# for multithreading
def get_blocks_from_ds(ds_id, chunk_id, blist, block_num, need_data, index):
    """get @blist form a chunk, chunk contain block_num blocks
    return a block list store in @need_data
    """
    data_list = []

    packet = GetChunkPacket(chunk_id, block_num, blist)
    msg = packet.get_message()
    sock = eventlet.connect((ds_id.split(':')[0],
                             int(ds_id.split(':')[1])))
    sock = sock.makefile('rw')
    send_command(sock, msg)
    recv = recv_command(sock)
    if recv['state'] != RET_SUCCESS:
        logging.error('get chunk from ds error: %s', recv['info'])
    else:
        data = recv_data(sock)
    sock.close()

    size = len(data)/len(blist)
    data_list = [data[i*size:(i+1)*size] for i in range(len(blist))]
    for i in range(len(blist)):
        need_data[index+i] = data_list[i]

    return data_list


class Client(object):
    """client to do request"""
    def __init__(self, config, test=False):
        """
        @config: ConfigParser() object
        @test: for unit test purpose
        """
        self._config = config

        # init logging
        logger = logging.getLogger()  # get the 'root' logger
        level = getattr(logging, config.get('log', 'log_level'))
        logger.setLevel(level)
        log_name = config.get('log', 'log_name')
        log_max_bytes = config.getint('log', 'log_max_bytes')
        log_file_num = config.getint('log', 'log_file_num')
        handler = logging.handlers.RotatingFileHandler(log_name,
                                                       maxBytes=log_max_bytes,
                                                       backupCount=log_file_num)
        log_format = logging.Formatter('%(levelname)-8s[%(asctime)s.%(msecs)d]'
                                       '<%(module)s> %(funcName)s:%(lineno)d:'
                                       ' %(message)s',
                                       datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(log_format)
        logger.addHandler(handler)

        # init mds information
        self._mds_ip = config.get('mds', 'mds_ip')
        self._mds_port = config.getint('mds', 'mds_port')

        # init file information
        self._packet_size = config.get('file', 'packet_size')
        self._block_size = config.get('file', 'block_size')

        # init current working directory
        self._cwd = '/'

        # init thread pool
        thread_num = config.getint('thread', 'thread_num')
        self.pool = eventlet.GreenPool(thread_num)

    def _get_sockfd_to_mds(self):
        sock = eventlet.connect((self._mds_ip, self._mds_port))
        return sock.makefile('rw')

    def _get_sockfd_to_ds(self, ds_ip, ds_port):
        sock = eventlet.connect((ds_ip, ds_port))
        return sock.makefile('rw')

    def _get_objkey_from_idx(self, filename, index):
        return '%s_obj%d' % (filename, index)

    def _get_chkkey_from_idx(self, filename, obj_index, chk_index):
        return '%s_obj%d_chk%d' % (filename, obj_index, chk_index)

    def _change_to_absolute_path(self, pathname):
        """change the path to absolute path in case of relative pathname"""
        # if not absolute path, add _cwd
        if not pathname.startswith('/'):
            pathname = self._cwd + pathname

        # delete '.' and '..'
        pathname = normpath(pathname)

        return pathname

    def mkdir(self, dirname):
        """make directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = MakeDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('mkdir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('mkdir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('mkdir response error: %s', info)
        return (state, info)

    def rmdir(self, dirname):
        """remove empty directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # check current directory in dirname
        if self._cwd.startswith(absolute_path):
            logging.info('can not remove directory contain cwd')
            state = RET_FAILURE
            info = 'can not remvoe directory contain cwd'
            return (state, info)

        # make request packet
        packet = RemoveDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('rmdir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('rmdir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('rmdir response error: %s', info)
        return (state, info)

    def listdir(self, dirname):
        """ls directory
        return: (state, subfiles)
            state: RET_FAILURE/RET_SUCCESS
            subfiles: [file1, dir1, ...]
        """
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = ListDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('list dir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('list dir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('list dir response error: %s', info)
        return (state, info)

    def chdir(self, dirname):
        """change directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = ValidDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('valid dir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('valid dir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('change dir error: %s', info)
        else:
            logging.info('change to dir: %s', absolute_path)
            self._cwd = absolute_path
        return (state, info)

    def getcwd(self):
        """get current working directory"""
        return self._cwd

    def statdir(self, dirname):
        """stat directory"""
        dirname = dirname.strip()
        if not dirname.endswith('/'):
            dirname += '/'

        # change dirname to absolute path
        absolute_path = self._change_to_absolute_path(dirname)
        if not absolute_path.endswith('/'):
            absolute_path += '/'

        # make request packet
        packet = StatusDirPacket(absolute_path)
        msg = packet.get_message()

        # get socket to mds
        sock = self._get_sockfd_to_mds()

        # send request
        logging.info('stat dir send msg: %s', msg)
        send_command(sock, msg)

        # recv response
        recv = recv_command(sock)
        logging.info('stat dir recv msg: %s', recv)
        sock.close()

        # check response and return
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.info('stat dir response error: %s', info)
        return (state, info)

    def _get_code_driver(self, code_info):
        """return a init code driver according to code_info """
        block_size = int(code_info['block_size'])
        code_type = code_info['type']

        code = None
        if code_type == CODE_RS:
            logging.info('code type rs')
            k = int(code_info['k'])
            m = int(code_info['m'])
            w = int(code_info['w'])
            packet_size = int(code_info['packet_size'])
            code = RSDriver(k=k, m=m, w=w, packet_size=packet_size,
                            block_size=block_size)
        elif code_type == CODE_CRS:
            logging.info('code type crs')
            k = int(code_info['k'])
            m = int(code_info['m'])
            w = int(code_info['w'])
            packet_size = int(code_info['packet_size'])
            code = CRSDriver(k=k, m=m, w=w, packet_size=packet_size,
                             block_size=block_size)
        elif code_type == CODE_Z:
            logging.info('code type zcode')
            k = int(code_info['k'])
            m = int(code_info['m'])
            packet_size = int(code_info['packet_size'])
            code = ZDriver(k=k, m=m, packet_size=packet_size,
                           block_size=block_size)
        return code

    def _send_chunk_to_ds(self, chunk_id, chunk_data, ds_id):
        packet = AddChunkPacket(chunk_id, len(chunk_data))
        msg = packet.get_message()
        sock = self._get_sockfd_to_ds(ds_id.split(':')[0],
                                      int(ds_id.split(':')[1]))
        send_command(sock, msg)

        # sending data
        send_data(sock, chunk_data)
        recv = recv_command(sock)
        logging.info('send chunk to ds recv: %s', recv)
        sock.close()
        return recv['state']

    def _add_file_commit(self, filename):
        """call after add file"""
        state = RET_SUCCESS
        info = 'ok'

        packet = AddFileCommitPacket(filename)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('add file commit :%s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('add file commit recv: %s', recv)
        sock.close()
        state = recv['state']
        if state == RET_FAILURE:
            info = 'add file commit error'

        if state == RET_SUCCESS:
            info = 'ok'
        return (state, info)

    def putfile(self, src_path, des_path, code_info={}):  # NOQA
        """put local @src_path file to remote @des_path with @code_info"""
        state = RET_SUCCESS
        info = 'ok'

        # get the local src_path information(filesize)
        try:
            filesize = getsize(src_path)
        except OSError:
            logging.error('no such file in local: %s', src_path)
            state = RET_FAILURE
            info = 'no such file in local'
            return (state, info)

        # set the fileinfo
        fileinfo = {}
        fileinfo['filesize'] = filesize

        code = {  # default code info
            'type': CODE_RS,
            'k': 2,
            'm': 2,
            'w': 8,
            'packet_size': self._packet_size,
            'block_size': self._block_size,
        }
        for (key, value) in code_info.items():
            code[key] = value
        fileinfo['code'] = code

        # call add file to mds with des_path and fileinfo
        filename = self._change_to_absolute_path(des_path)
        packet = AddFilePacket(filename, fileinfo)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('put file send to mds: %s', msg)
        send_command(sock, msg)

        # recv the mds response
        recv = recv_command(sock)
        sock.close()
        logging.info('put file recv from mds: %s', recv)

        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.error('put file recv from mds error')
            return (state, info)

        # get the objects and chunks ds information
        object_size = info['object_size']
        object_num = info['object_num']
        chunk_size = info['chunk_size']
        ds_list = info['objects']
        driver = self._get_code_driver(code)
        fd = open(src_path, 'r')

        for obj_idx in range(object_num):
            # split file to object
            data = fd.read(object_size)
            if len(data) < object_size:
                data += ' ' * (object_size - len(data))

            # encode object to chunks
            (state, chunks) = driver.encode(data)
            if state == RET_FAILURE:
                logging.error('driver encode error')
                info = 'driver encode error'
                return (state, info)

            data_chunk_num = driver.get_data_chunk_num()
            parity_chunk_num = driver.get_parity_chunk_num()
            # put chunks to ds
            for data_idx in range(data_chunk_num):
                chunk_id = self._get_chkkey_from_idx(filename,
                                                     obj_idx,
                                                     data_idx)
                chunk_data = chunks[0][data_idx*chunk_size:
                                       (data_idx+1)*chunk_size]
                ds_id = ds_list[obj_idx][data_idx]
                self.pool.spawn_n(self._send_chunk_to_ds, chunk_id,
                                  chunk_data, ds_id)

            for parity_idx in range(parity_chunk_num):
                chunk_id = self._get_chkkey_from_idx(filename,
                                                     obj_idx,
                                                     parity_idx+data_chunk_num)
                chunk_data = chunks[1][parity_idx*chunk_size:
                                       (parity_idx+1)*chunk_size]
                ds_id = ds_list[obj_idx][parity_idx+data_chunk_num]
                self.pool.spawn_n(self._send_chunk_to_ds, chunk_id,
                                  chunk_data, ds_id)
            # wait for write end
            self.pool.waitall()

        fd.close()

        # commit to mds
        if state == RET_SUCCESS:
            (state, info) = self._add_file_commit(filename)

        if state == RET_SUCCESS:
            info = 'ok'
        return (state, info)

    def delfile(self, path):
        """delete a file"""
        filename = self._change_to_absolute_path(path)

        # delete meta data in mds
        packet = DeleteFilePacket(filename)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('stat file send to mds: %s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('stat file recv %s', recv)
        sock.close()
        state = recv['state']
        info = recv['info']

        # delete data chunk in ds
        for item in info:
            chunk_id = item[0]
            ds_id = item[1]

            packet = DeleteChunkPacket(chunk_id)
            msg = packet.get_message()
            sock = self._get_sockfd_to_ds(ds_id.split(':')[0],
                                          int(ds_id.split(':')[1]))
            send_command(sock, msg)
            recv = recv_command(sock)
            state = recv['state']
            if state == RET_FAILURE:
                logging.error('delete chunk in ds: %s %s', chunk_id, ds_id)
                info = 'delete chunk ds error'

        if state == RET_SUCCESS:
            info = 'ok'
        return (state, info)

    def statfile(self, path):
        """stat a file"""
        filename = self._change_to_absolute_path(path)
        packet = StatFilePacket(filename)
        msg = packet.get_message()

        sock = self._get_sockfd_to_mds()
        logging.info('stat file send to mds: %s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('stat file recv %s', recv)
        sock.close()
        state = recv['state']
        info = recv['info']
        return (state, info)

    def getfile(self, des_path, local_path, repair_flag=False):
        """get file from @des_path to @local_path,
        if repair_flag is True, repair missing chunks
        """
        logging.info('get file: %s to %s', des_path, local_path)
        # filename = self._change_to_absolute_path(des_path)
        state = RET_SUCCESS
        info = 'ok'

        # TODO

        if state == RET_SUCCESS:
            info = 'ok'
        return (state, info)

    def getobject(self, object_id, local_path, repair_flag=False):
        """get object from @des_path to @local_path,
        if repair_flag is True, repair missing objects
        """
        logging.info('get object: %s to %s', object_id, local_path)
        state = RET_SUCCESS
        info = 'ok'

        packet = GetObjPacket(object_id)
        msg = packet.get_message()
        sock = self._get_sockfd_to_mds()
        send_command(sock, msg)

        recv = recv_command(sock)
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.error('get object recv from mds: %s', recv)
            return (state, info)

        # init the code driver
        driver = self._get_code_driver(info['code'])
        data_chunk_num = driver.get_data_chunk_num()

        # check the chunk status
        available_chunk = []
        missing_chunk = []
        chunks_info = info['chunks']
        chunk_num = info['chunk_num']
        for index in range(chunk_num):
            item_info = chunks_info[index]
            state = item_info['status']
            if item_info['ds_info']['status'] != DS_CONNECTED:
                state == CHUNK_MISSING

            if state == CHUNK_OK:
                chk_id = '%s_chk%d' % (object_id, index)
                ds_id = item_info['ds_id']
                available_chunk.append((chk_id, ds_id))
            else:
                missing_chunk.append(index)

        # set the available_chunk and available_list
        if len(available_chunk) < data_chunk_num:
            logging.error('available_chunk less than data chunk num')
            info = 'available_chunk < data_chunk_num'
            return (RET_FAILURE, info)

        task = []
        block_num = driver.get_block_num()
        block_list = []
        for index in range(data_chunk_num):
            ds_id = available_chunk[index][1]
            chk_id = available_chunk[index][0]
            chk_index = int(chk_id.rsplit('_chk')[1])
            blist = range(block_num)
            task.append((ds_id, chk_id, blist, block_num))
            block_list += range(chk_index*block_num, (chk_index+1)*block_num)

        task_data = block_list[:]

        # multithreading read blocks
        index = 0
        for item in task:
            self.pool.spawn_n(get_blocks_from_ds, item[0], item[1], item[2],
                              item[3], task_data, index)
            index += len(item[2])
        self.pool.waitall()

        # decode object
        (state, data) = driver.decode(task_data, block_list)
        if state == RET_FAILURE:
            logging.error('decode error')
            info = 'decode error'
            return (RET_FAILURE, info)

        # write to disk
        fd = open(local_path, 'w')
        fd.write(data)
        fd.close()

        if state == RET_SUCCESS:
            info = 'ok'

        return (state, info)

    def _get_one_chunk_from_ds(self, ds_id, chunk_id):
        """get one chunk"""
        data = ''

        packet = GetChunkPacket(chunk_id, 1, [0])  # get all blocks in one chunk
        msg = packet.get_message()
        sock = self._get_sockfd_to_ds(ds_id.split(':')[0],
                                      int(ds_id.split(':')[1]))
        send_command(sock, msg)
        recv = recv_command(sock)
        if recv['state'] != RET_SUCCESS:
            logging.error('get chunk from ds error: %s', recv['info'])
        else:
            data = recv_data(sock)
        sock.close()

        return data

    def _get_blocks_from_ds(self, ds_id, chunk_id, blist, block_num):
        """get @blist form a chunk, chunk contain block_num blocks
        return a block list
        """
        data_list = []

        packet = GetChunkPacket(chunk_id, block_num, blist)
        msg = packet.get_message()
        sock = self._get_sockfd_to_ds(ds_id.split(':')[0],
                                      int(ds_id.split(':')[1]))
        send_command(sock, msg)
        recv = recv_command(sock)
        if recv['state'] != RET_SUCCESS:
            logging.error('get chunk from ds error: %s', recv['info'])
        else:
            data = recv_data(sock)
        sock.close()

        size = len(data)/len(blist)
        data_list = [data[i*size:(i+1)*size] for i in range(len(blist))]

        return data_list

    def _degrade_get_chunk(self, stripe_info, chunk_id):  # NOQA
        """repair chunk from other chunks"""
        data = ''
        driver = self._get_code_driver(stripe_info['code'])

        available_chunk = {}
        missing_chunk = []
        object_id = chunk_id.rsplit('_chk')[0]
        chunks_info = stripe_info['chunks']
        chunk_num = len(chunks_info)
        for index in range(chunk_num):
            item_info = chunks_info[index]
            state = item_info['status']
            if item_info['ds_info']['status'] != DS_CONNECTED:
                state = CHUNK_MISSING

            if state == CHUNK_OK:
                chk_id = '%s_chk%d' % (object_id, index)
                ds_id = item_info['ds_id']
                available_chunk[chk_id] = ds_id
            else:
                missing_chunk.append(index)

        repair_indexes = []
        exclude_indexes = []
        code_type = driver.get_type()
        chunk_index = int(chunk_id.rsplit('_chk')[1])
        if code_type == CODE_RS:
            repair_indexes.append(chunk_index)
            exclude_indexes = missing_chunk
        elif code_type == CODE_CRS:
            repair_indexes = range(chunk_index*driver.w,
                                   (chunk_index+1)*driver.w)
            for index in missing_chunk:
                mlist = range(index*driver.w, (index+1)*driver.w)
                exclude_indexes += mlist
        elif code_type == CODE_Z:
            repair_indexes = chunk_index
            if len(missing_chunk) > 1:
                logging.error('zcode missing chunk > 1')
                return data

        (state, need_list) = driver.repair_needed_blocks(repair_indexes,
                                                         exclude_indexes)

        if state == RET_FAILURE:
            logging.error('repair needed blocks return error')
            return data

        # get need data from chunks
        block_num = driver.get_block_num()
        blist = []
        chunk_idx = -1   # start num
        task = []
        for index in need_list:
            new_chunk_idx = index / block_num
            if chunk_idx < 0:
                chunk_idx = new_chunk_idx
            if new_chunk_idx != chunk_idx:
                chk_id = '%s_chk%d' % (object_id, chunk_idx)
                ds_id = available_chunk[chk_id]
                task.append([ds_id, chk_id, blist, block_num])
                blist = []
                chunk_idx = new_chunk_idx
                blist.append(index % block_num)
            else:
                blist.append(index % block_num)

        # get last chunk blocks
        chk_id = '%s_chk%d' % (object_id, chunk_idx)
        ds_id = available_chunk[chk_id]
        task.append([ds_id, chk_id, blist, block_num])

        task_data = need_list[:]

        # multithreading read blocks
        index = 0
        for item in task:
            self.pool.spawn_n(get_blocks_from_ds, item[0], item[1], item[2],
                              item[3], task_data, index)
            index += len(item[2])
        self.pool.waitall()
        need_data = task_data

        # repair chunk
        (state, data) = driver.repair(need_data, need_list, repair_indexes)
        if state == RET_FAILURE:
            logging.error('repair error')
            data = ''

        return data

    def getchunk(self, chunk_id, local_path, repair_flag=False):
        """get chunk from @des_path to @local_path,
        if repair_flag is True, repair missing chunks
        """
        logging.info('get chunk: %s to %s', chunk_id, local_path)
        state = RET_SUCCESS
        info = 'ok'

        packet = GetChkPacket(chunk_id)
        msg = packet.get_message()
        sock = self._get_sockfd_to_mds()
        send_command(sock, msg)

        recv = recv_command(sock)
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.error('get chunk recv from mds: %s', recv)
            return (state, info)

        # check chunk status
        chunk_idx = int(chunk_id.rsplit('_chk')[1])
        chunks_info = info['chunks']
        chunk_info = chunks_info[chunk_idx]
        chunk_state = chunk_info['status']
        ds_id = chunk_info['ds_id']

        if chunk_info['ds_info']['status'] != DS_CONNECTED:
            chunk_state = CHUNK_MISSING

        if chunk_state != CHUNK_OK:
            # degrade chunk get
            data = self._degrade_get_chunk(recv['info'], chunk_id)
        else:
            # get data from chunk
            data = self._get_one_chunk_from_ds(ds_id, chunk_id)

        if not data:
            info = 'get chunk from ds error'
            state == RET_FAILURE
        else:
            fd = open(local_path, 'w')
            fd.write(data)
            fd.close()

        if state == RET_SUCCESS:
            info = 'ok'
        return (state, info)

    def get_chunk_ds_id(self, chunk_id):
        ds_ip = ''
        ds_port = 0
        logging.info('get chunk: %s', chunk_id)

        packet = GetChkPacket(chunk_id)
        msg = packet.get_message()
        sock = self._get_sockfd_to_mds()
        send_command(sock, msg)

        recv = recv_command(sock)
        state = recv['state']
        info = recv['info']
        if state == RET_FAILURE:
            logging.error('get chunk recv from mds: %s', recv)
            return (ds_ip, ds_port)

        # get chunk ds_id
        chunk_idx = int(chunk_id.rsplit('_chk')[1])
        chunks_info = info['chunks']
        chunk_info = chunks_info[chunk_idx]
        ds_id = chunk_info['ds_id']
        ds_ip = ds_id.split(':')[0]
        ds_port = int(ds_id.split(':')[1])

        return (ds_ip, ds_port)

    def report_ds(self, ds_ip, ds_port, status=DS_CONNECTED):
        info = {
            'status': status,
        }
        packet = ReportDSPacket(ds_ip, ds_port, info)
        msg = packet.get_message()
        sock = self._get_sockfd_to_mds()

        logging.info('report ds :%s', msg)
        send_command(sock, msg)

        recv = recv_command(sock)
        logging.info('reprot ds recv: %s', recv)
        sock.close()

        return recv['state']
