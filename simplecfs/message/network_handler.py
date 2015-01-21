# -*- coding: utf-8 -*-
"""
handle network sending and receiving data
"""
import logging

from simplecfs.common.parameters import DATA_FRAME_SIZE
from simplecfs.message.packet import pack, unpack


def send_command(socket_fd, message):
    """
    send command message packet over socket
    @socket_fd(socket.makefile('rw'))
    @message: message of dict format
    """
    logging.info('send command packet')

    msg = pack(message)
    socket_fd.write('%d\n%s' % (len(msg), msg))
    socket_fd.flush()


def recv_command(socket_fd):
    """
    receive command message packet from socket_fd
    return dict command
    """
    logging.info('recv command packet')

    line = socket_fd.readline()
    command_length = int(line)
    command = socket_fd.read(command_length)

    logging.info("recv command: %s", command)
    return unpack(command)


def send_data(socket_fd, data):
    """send data packet over socket_fd"""
    logging.info('sending data packet')

    socket_fd.write('%d\n%s' % (len(data), data))
    socket_fd.flush()


def recv_data(socket_fd, frame_size=DATA_FRAME_SIZE):
    """receive data packet from socket_fd"""
    logging.info('receiving data packet')

    data = []
    line = socket_fd.readline()
    length = int(line)
    while length > 0:
        recv_ = socket_fd.read(min(length, frame_size))
        data.append(recv_)
        length -= len(recv_)
    data = b''.join(data)

    return data
