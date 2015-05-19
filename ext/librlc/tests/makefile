#CC = gcc -O3
CC = gcc 
CFLAGS = -g -Wall -msse4.1 -DINTEL_SSE4 -msse4.2 -DINTEL_SSE4 -fPIC

CFILES = $(wildcard *.c)
PROGS =	$(patsubst %.c,%.test,$(CFILES))

all: $(PROGS)


%.test: %.o
		$(CC) $(CFLAGS) -o $@ $< ../*.o  ../gf_complete.a -lpthread

.c.o:
		$(CC) $(CFLAGS) -c $*.c

clean:
		rm -f *.o *.test
