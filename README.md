## SimpleCFS

a simple coded file system.

## Dependence

1. gf\_complete
2. librlc

## Install
    
    git clone --recursive http://192.168.0.19/hustlijian/simplecfs.git
    
    cd ext/gf-complete
	./autogen.sh
	./configure
	make
	cp src/.libs/libgf_complete.a ../librlc/gf_complete.a

	cd ../librlc
	make

## Test

    python setup.py test

## Run

### MDS

    redis-server # start the redis-server

    python ./mds.py

### DS

    python ./ds.py

### Client

    python ./client.py

## Example
