# SimpleCFS

A Simple Coded File System, write in python.

# Dependence

1. python-dev
2. python 2.7
3. gcc -msse -msse2 flag

# Tested OS

1. Mac OSX
2. Ubuntu 12.04+

# Use

## Install
    
    git clone http://github.com/hustlijian/simplecfs.git
    cd simplecfs  # change directory to simplecfs

    sudo pip install -r requirements.txt
    sudo apt-get install python-dev # yum install python-devel
    
    make

## Test

    make test

## Run

change directory to `bin`

### MDS

    redis-server # start the redis-server

    python ./mds.py

### DS

    python ./ds.py

### Client

    python ./client.py

## Example
