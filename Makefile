build:
	# 编译gf-complete
	cd ext/gf-complete;./autogen.sh;./configure;make clean;make;cp src/.libs/libgf_complete.a ../librlc/gf_complete.a
	# 编译librlc
	cd ext/librlc;make clean; make
	# 编译redis
	cd ext/redis;make clean; make MALLOC=libc

test:
	@cd ext/redis/src; rm dump.rdb;./redis-server > /dev/null &
	python setup.py test
	@pkill redis-server

all: build

.PHONY:clean

clean:
	# gf-complete
	cd ext/gf-complete;make clean
	# 编译librlc
	cd ext/librlc;make clean
	# 编译redis
	cd ext/redis;make clean
