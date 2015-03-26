## SimpleCFS

a simple coded file system.

## Dependence

1. gf\_complete
2. librlc
3. nose
4. eventlet
5. greenlet
6. redis

## Install
    
    git clone --recursive http://192.168.0.19/hustlijian/simplecfs.git
    cd simplecfs  # change directory to simplecfs

    sudo pip install -r requirements.txt
    
    make

## Test

    make test

## Run

### MDS

    redis-server # start the redis-server

    python ./mds.py

### DS

    python ./ds.py

### Client

    python ./client.py

## Example
