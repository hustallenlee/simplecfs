#!/usr/bin/env python
"""
python call liblrc code
"""
import ctypes
from math import pow

librlc = ctypes.CDLL('../librlc.so')


def test_rs():
    k = 4
    m = 2
    w = 8
    packet_size = 1024
    src_filename = './test.txt'
    encoded_data_file = './data/py-data.txt'
    encoded_parity_file = './data/py-parity.txt'
    decoded_file = './data/py-decode.txt'
    repair_data_file = './data/py-repair-data.txt'
    repair_parity_file = './data/py-repair-parity.txt'

    # encode
    orig_data = open(src_filename, "r").read()
    data_len = len(orig_data)
    print 'data len %d' % data_len
    encoded_data = ctypes.pointer(ctypes.c_char_p())
    encoded_parity = ctypes.pointer(ctypes.c_char_p())
    chunk_len = ctypes.c_int(1)
    librlc.librlc_rs_encode(k, m, w, packet_size, orig_data, data_len,
                            ctypes.byref(encoded_data),
                            ctypes.byref(encoded_parity),
                            ctypes.byref(chunk_len))
    print 'chunk len %d' % chunk_len.value
    print 'encoded data:'
    data = ctypes.string_at(encoded_data, k*(chunk_len.value))
    print 'len data: %d' % len(data)
    parity = ctypes.string_at(encoded_parity, m*(chunk_len.value))
    print 'parity data: %d' % len(parity)
    open(encoded_data_file, 'w').write(data)
    open(encoded_parity_file, 'w').write(parity)
    librlc.librlc_rs_encode_cleanup(encoded_data, encoded_parity)

    # decode
    encoded_data = open(encoded_data_file, 'r').read()
    encoded_parity = open(encoded_parity_file, 'r').read()
    Alist = ctypes.c_int * k
    data_list = Alist()
    for i in range(0, k-1):
        data_list[i] = i
    data_list[k-1] = k
    print 'data_list ',
    print data_list
    chunk_len = int(chunk_len.value)
    available_data = encoded_data[:(k-1)*chunk_len] + encoded_parity[:chunk_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    librlc.librlc_rs_decode(k, m, w, packet_size, available_data, data_list,
                            k, chunk_len, ctypes.byref(out_data))
    data = ctypes.string_at(out_data, data_len)
    open(decoded_file, 'w').write(data)
    librlc.librlc_rs_decode_cleanup(out_data)

    # repair
    encoded_data = open(encoded_data_file, 'r').read()
    encoded_parity = open(encoded_parity_file, 'r').read()
    Alist = ctypes.c_int * k
    data_list = Alist()
    for i in range(0, k-1):
        data_list[i] = i
    data_list[k-1] = k
    print 'data_list ',
    print data_list
    available_data = encoded_data[:(k-1)*chunk_len] + encoded_parity[:chunk_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    Blist = ctypes.c_int * m
    repair_list = Blist()
    repair_list[0] = k-1
    for i in range(1, m):
        repair_list[i] = i+k
    librlc.librlc_rs_repair(k, m, w, packet_size, available_data, data_list,
                            k, chunk_len, repair_list, m,
                            ctypes.byref(out_data))
    data = ctypes.string_at(out_data, m*chunk_len)

    open(repair_data_file, 'w').write(
        encoded_data[:(k-1)*chunk_len]+data[:chunk_len])
    open(repair_parity_file, 'w').write(
        encoded_parity[:chunk_len]+data[chunk_len:])
    librlc.librlc_rs_repair_cleanup(out_data)

def test_crs():
    k = 4
    m = 2
    w = 4
    packet_size = 1024
    src_filename = './test.txt'
    encoded_data_file = './data/py-crs-data.txt'
    encoded_parity_file = './data/py-crs-parity.txt'
    decoded_file = './data/py-crs-decode.txt'
    repair_data_file = './data/py-crs-repair-data.txt'
    repair_parity_file = './data/py-crs-repair-parity.txt'

    # encode
    orig_data = open(src_filename, "r").read()
    data_len = len(orig_data)
    print 'data len %d' % data_len
    encoded_data = ctypes.pointer(ctypes.c_char_p())
    encoded_parity = ctypes.pointer(ctypes.c_char_p())
    chunk_len = ctypes.c_int(1)
    librlc.librlc_crs_encode(k, m, w, packet_size, orig_data, data_len,
                            ctypes.byref(encoded_data),
                            ctypes.byref(encoded_parity),
                            ctypes.byref(chunk_len))
    print 'chunk len %d' % chunk_len.value
    print 'encoded data:'
    data = ctypes.string_at(encoded_data, k*w*(chunk_len.value))
    print 'len data: %d' % len(data)
    parity = ctypes.string_at(encoded_parity, m*w*(chunk_len.value))
    print 'parity data: %d' % len(parity)
    open(encoded_data_file, 'w').write(data)
    open(encoded_parity_file, 'w').write(parity)
    librlc.librlc_crs_encode_cleanup(encoded_data, encoded_parity)

    # decode
    print 'Decode: '
    encoded_data = open(encoded_data_file, 'r').read()
    encoded_parity = open(encoded_parity_file, 'r').read()
    Alist = ctypes.c_int * (k*w)
    data_list = Alist()
    for i in range(0, k*w-1):
        data_list[i] = i
    data_list[k*w-1] = k*w
    print 'data_list ',
    print data_list
    chunk_len = int(chunk_len.value)
    available_data = encoded_data[:(k*w-1)*chunk_len] + encoded_parity[:chunk_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    librlc.librlc_crs_decode(k, m, w, packet_size, available_data, data_list,
                            k*w, chunk_len, ctypes.byref(out_data))
    print 'crs decode end'
    data = ctypes.string_at(out_data, data_len)
    open(decoded_file, 'w').write(data)
    librlc.librlc_crs_decode_cleanup(out_data)

    # repair
    print 'Repair: '
    encoded_data = open(encoded_data_file, 'r').read()
    encoded_parity = open(encoded_parity_file, 'r').read()
    Alist = ctypes.c_int * (k*w)
    data_list = Alist()
    for i in range(0, k*w-1):
        data_list[i] = i
    data_list[k*w-1] = k*w
    print 'data_list ',
    print data_list
    available_data = encoded_data[:(k*w-1)*chunk_len] + encoded_parity[:chunk_len]
    out_data = ctypes.pointer(ctypes.c_char_p())
    Blist = ctypes.c_int * (m*w)
    repair_list = Blist()
    repair_list[0] = k*w-1
    for i in range(1, m*w):
        repair_list[i] = i+k*w
    librlc.librlc_crs_repair(k, m, w, packet_size, available_data, data_list,
                            k*w, chunk_len, repair_list, m*w,
                            ctypes.byref(out_data))
    data = ctypes.string_at(out_data, m*w*chunk_len)

    open(repair_data_file, 'w').write(
        encoded_data[:(k*w-1)*chunk_len]+data[:chunk_len])
    open(repair_parity_file, 'w').write(
        encoded_parity[:chunk_len]+data[chunk_len:])
    librlc.librlc_crs_repair_cleanup(out_data)


def test_zcode():
    m = 2
    k = 4
    node = 0
    packet_size = 1024
    src_filename = './test.txt'
    encoded_data_file = './data/py-z-data.txt'
    encoded_parity_file = './data/py-z-parity.txt'
    repair_data_file = './data/py-z-repair-data.txt'

    # encode
    orig_data = open(src_filename, "r").read()
    data_len = len(orig_data)
    print 'data len %d' % data_len
    encoded_data = ctypes.pointer(ctypes.c_char_p())
    encoded_parity = ctypes.pointer(ctypes.c_char_p())
    chunk_len = ctypes.c_int(1)
    librlc.librlc_z_encode(k, m, packet_size, orig_data, data_len,
                            ctypes.byref(encoded_data),
                            ctypes.byref(encoded_parity),
                            ctypes.byref(chunk_len))
    print 'chunk len %d' % chunk_len.value
    print 'encoded data:'
    r = int(pow(m, k-1))
    data = ctypes.string_at(encoded_data, int(k*r*(chunk_len.value)))
    print 'len data: %d' % len(data)
    parity = ctypes.string_at(encoded_parity, int(m*r*(chunk_len.value)))
    print 'parity data: %d' % len(parity)
    open(encoded_data_file, 'w').write(data)
    open(encoded_parity_file, 'w').write(parity)
    librlc.librlc_z_encode_cleanup(encoded_data, encoded_parity)

    # decode
    # no decode in zcode, use original data
    print 'Decode: '

    # repair
    print 'Repair: '
    encoded_data = open(encoded_data_file, 'r').read()
    encoded_parity = open(encoded_parity_file, 'r').read()
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
        available_data += all_data[chunk_len.value*item:chunk_len.value*(item+1)]
    out_data = ctypes.pointer(ctypes.c_char_p())
    librlc.librlc_z_repair(k, m, packet_size, available_data, repair_list,
                            repair_num, chunk_len, node,
                            ctypes.byref(out_data))
    data = ctypes.string_at(out_data, r*chunk_len.value)

    new_data = encoded_data[:(node*r)*chunk_len.value]
    new_data += data
    new_data += encoded_data[(node+1)*r*chunk_len.value:]
    open(repair_data_file, 'w').write(new_data)
    librlc.librlc_z_repair_cleanup(out_data)

if __name__ == '__main__':
    test_rs()
    test_crs()
    test_zcode()
