#!/usr/bin/env python
"""
python call librlc code and test the coders
"""

import ctypes
from math import pow
from nose.tools import eq_

import os

DATA_LENGTH = 6660000
orig_data = os.urandom(DATA_LENGTH)
librlc = ctypes.CDLL('ext/librlc/librlc.so')


def test_rs(k=4, m=2, w=8, packet_size=1024):
    """test the rs code"""
    # encode
    data_len = DATA_LENGTH
    print 'data len %d' % data_len
    encoded_data = ctypes.pointer(ctypes.c_char_p())
    encoded_parity = ctypes.pointer(ctypes.c_char_p())
    block_len = ctypes.c_int(1)
    librlc.librlc_rs_encode(k, m, w, packet_size, orig_data, data_len,
                            ctypes.byref(encoded_data),
                            ctypes.byref(encoded_parity),
                            ctypes.byref(block_len))
    print 'chunk len %d' % block_len.value
    print 'encoded data:'
    data = ctypes.string_at(encoded_data, k*(block_len.value))
    print 'len data: %d' % len(data)
    parity = ctypes.string_at(encoded_parity, m*(block_len.value))
    print 'parity data: %d' % len(parity)
    librlc.librlc_rs_encode_cleanup(encoded_data, encoded_parity)

    encoded_data_value = data
    encoded_parity_value = parity

    # decode
    encoded_data = encoded_data_value
    encoded_parity = encoded_parity_value
    Alist = ctypes.c_int * k
    data_list = Alist()
    for i in range(0, k-1):
        data_list[i] = i
    data_list[k-1] = k
    print 'data_list ',
    print data_list
    block_len = int(block_len.value)
    available_data = encoded_data[:(k-1)*block_len] + encoded_parity[:block_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    librlc.librlc_rs_decode(k, m, w, packet_size, available_data, data_list,
                            k, block_len, ctypes.byref(out_data))
    data = ctypes.string_at(out_data, data_len)
    librlc.librlc_rs_decode_cleanup(out_data)

    decoded_data = data
    eq_(decoded_data, orig_data)

    # repair
    encoded_data = encoded_data_value
    encoded_parity = encoded_parity_value
    Alist = ctypes.c_int * k
    data_list = Alist()
    for i in range(0, k-1):
        data_list[i] = i
    data_list[k-1] = k
    print 'data_list ',
    print data_list
    available_data = encoded_data[:(k-1)*block_len] + encoded_parity[:block_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    Blist = ctypes.c_int * m
    repair_list = Blist()
    repair_list[0] = k-1
    for i in range(1, m):
        repair_list[i] = i+k
    librlc.librlc_rs_repair(k, m, w, packet_size,
                            available_data, data_list,
                            k, block_len, repair_list, m,
                            ctypes.byref(out_data))
    data = ctypes.string_at(out_data, m*block_len)

    repair_data = encoded_data[:(k-1)*block_len]+data[:block_len]
    repair_parity = encoded_parity[:block_len]+data[block_len:]
    librlc.librlc_rs_repair_cleanup(out_data)

    eq_(repair_data, encoded_data_value)
    eq_(repair_parity, encoded_parity_value)


def test_crs(k=4, m=2, w=4, packet_size=1024):
    # encode
    data_len = DATA_LENGTH
    print 'data len %d' % data_len
    encoded_data = ctypes.pointer(ctypes.c_char_p())
    encoded_parity = ctypes.pointer(ctypes.c_char_p())
    block_len = ctypes.c_int(1)
    librlc.librlc_crs_encode(k, m, w, packet_size, orig_data, data_len,
                             ctypes.byref(encoded_data),
                             ctypes.byref(encoded_parity),
                             ctypes.byref(block_len))
    print 'chunk len %d' % block_len.value
    print 'encoded data:'
    data = ctypes.string_at(encoded_data, k*w*(block_len.value))
    print 'len data: %d' % len(data)
    parity = ctypes.string_at(encoded_parity, m*w*(block_len.value))
    print 'parity data: %d' % len(parity)
    encoded_data_value = data
    encoded_parity_value = parity
    librlc.librlc_crs_encode_cleanup(encoded_data, encoded_parity)

    # decode
    print 'Decode: '
    encoded_data = encoded_data_value
    encoded_parity = encoded_parity_value
    Alist = ctypes.c_int * (k*w)
    data_list = Alist()
    for i in range(0, k*w-1):
        data_list[i] = i
    data_list[k*w-1] = k*w
    print 'data_list ',
    print data_list
    block_len = int(block_len.value)
    available_data = encoded_data[:(k*w-1)*block_len] +\
        encoded_parity[:block_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    librlc.librlc_crs_decode(k, m, w, packet_size, available_data,
                             data_list,
                             k*w, block_len, ctypes.byref(out_data))
    print 'crs decode end'
    data = ctypes.string_at(out_data, data_len)
    decoded_data = data
    librlc.librlc_crs_decode_cleanup(out_data)

    eq_(orig_data, decoded_data)

    # repair
    print 'Repair: '
    encoded_data = encoded_data_value
    encoded_parity = encoded_parity_value
    Alist = ctypes.c_int * (k*w)
    data_list = Alist()
    for i in range(0, k*w-1):
        data_list[i] = i
    data_list[k*w-1] = k*w
    print 'data_list ',
    print data_list
    available_data = encoded_data[:(k*w-1)*block_len] +\
        encoded_parity[:block_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    Blist = ctypes.c_int * (m*w)
    repair_list = Blist()
    repair_list[0] = k*w-1
    for i in range(1, m*w):
        repair_list[i] = i+k*w

    librlc.librlc_crs_repair(k, m, w, packet_size, available_data,
                             data_list,
                             k*w, block_len, repair_list, m*w,
                             ctypes.byref(out_data))
    data = ctypes.string_at(out_data, m*w*block_len)

    repair_data_value = encoded_data[:(k*w-1)*block_len]+data[:block_len]
    repair_parity_value = encoded_parity[:block_len]+data[block_len:]
    librlc.librlc_crs_repair_cleanup(out_data)

    eq_(repair_data_value, encoded_data_value)
    eq_(repair_parity_value, encoded_parity_value)


def test_zcode(k=4, m=2, packet_size=1024):
    node = 0  # node num to be repaired

    # encode
    data_len = DATA_LENGTH
    print 'data len %d' % data_len
    encoded_data = ctypes.pointer(ctypes.c_char_p())
    encoded_parity = ctypes.pointer(ctypes.c_char_p())
    block_len = ctypes.c_int(1)
    librlc.librlc_z_encode(k, m, packet_size, orig_data, data_len,
                           ctypes.byref(encoded_data),
                           ctypes.byref(encoded_parity),
                           ctypes.byref(block_len))
    print 'chunk len %d' % block_len.value
    print 'encoded data:'
    r = int(pow(m, k-1))
    data = ctypes.string_at(encoded_data, int(k*r*(block_len.value)))
    print 'len data: %d' % len(data)
    parity = ctypes.string_at(encoded_parity, int(m*r*(block_len.value)))
    print 'parity data: %d' % len(parity)
    encoded_data_value = data
    encoded_parity_value = parity
    librlc.librlc_z_encode_cleanup(encoded_data, encoded_parity)

    # decode
    # no decode in zcode, use original data
    print 'Decode: '
    block_len = int(block_len.value)

    # repair
    print 'Repair: '
    encoded_data = encoded_data_value
    encoded_parity = encoded_parity_value
    repair_num = (m+k-1)*r/m
    Alist = ctypes.c_int * repair_num
    repair_list = Alist()
    librlc.librlc_z_repair_chunk_needed(m, k, node, repair_num, repair_list)
    print 'repair_list ',
    print repair_list
    available_data = ''
    all_data = encoded_data+encoded_parity
    for item in repair_list:
        print item,
        available_data += all_data[block_len*item:
                                   block_len*(item+1)]
    out_data = ctypes.pointer(ctypes.c_char_p())
    librlc.librlc_z_repair(k, m, packet_size, available_data, repair_list,
                           repair_num, block_len, node,
                           ctypes.byref(out_data))
    data = ctypes.string_at(out_data, r*block_len)

    new_data = encoded_data[:(node*r)*block_len]
    new_data += data
    new_data += encoded_data[(node+1)*r*block_len:]
    repair_data = new_data
    librlc.librlc_z_repair_cleanup(out_data)
    eq_(repair_data, encoded_data_value)
