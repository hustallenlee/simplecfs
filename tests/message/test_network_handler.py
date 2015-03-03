# -*- coding: utf-8 -*-
"""
network hander unittest
"""
import eventlet
from nose.tools import eq_

from simplecfs.message.network_handler import (recv_command, recv_data,
                                               send_command, send_data)


POOL = eventlet.GreenPool(10)


def start_accept(server):
    """start server in ip and port"""
    sock, address = server.accept()
    sock_fd = sock.makefile('rw')

    # receive data or command
    data = recv_data(sock_fd)

    # sent the same data or command
    send_data(sock_fd, data)
    sock_fd.close()


def test_command():
    """test send and recv command"""
    ip = '127.0.0.1'
    port = 8899
    command = 'command'

    # start server to receive command
    print 'start server'
    server = eventlet.listen((ip, port))
    POOL.spawn_n(start_accept, server)

    # connect to server
    print 'start connect'
    client = eventlet.connect((ip, port))
    client_fd = client.makefile('rw')

    # send command
    send_command(client_fd, command)

    # receive response(same with send command)
    response = recv_command(client_fd)

    # check response
    eq_(response, command)


def test_data():
    """test send and recv data"""
    ip = '127.0.0.1'
    port = 8899
    data = 'data'

    # start server to receive data
    print 'start server'
    server = eventlet.listen((ip, port))
    POOL.spawn_n(start_accept, server)

    # connect to server
    print 'start connect'
    client = eventlet.connect((ip, port))
    client_fd = client.makefile('rw')

    # send data
    send_data(client_fd, data)

    # receive response(same with send data)
    response = recv_data(client_fd)

    # check response
    eq_(response, data)
