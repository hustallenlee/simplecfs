build:
	cd ext/gf-complete;./autogen.sh;./configure;make;cp src/.libs/libgf_complete.a ../librlc/gf_complete.a
	# 编译librlc
	cd ext/librlc;make
	# 编译redis
	cd ext/redis;make

test:
	@cd ext/redis/src;./redis-server > /dev/null &
	python setup.py test
	@pkill redis-server

all: build
