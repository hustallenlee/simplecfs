AR = ar
CC = gcc -g
CFLAGS = -O3 -Wall -Wextra -mmmx -msse -DINTEL_SSE -msse2 -DINTEL_SSE2 -msse3 -DINTEL_SSE3 -mssse3 -msse4.1 -DINTEL_SSE4 -msse4.2 -DINTEL_SSE4 -fPIC

OUTPUT := librlc.a

SOURCE := $(wildcard *.c)
OBJS := $(patsubst %.c, %.o, $(SOURCE))

ifndef segment_size
	segment_size=256
endif

%.o:%.c
	$(CC) $(CFLAGS) -c $< -o $@

all: preprocess $(OBJS) $(OUTPUT)

preprocess:
	@if [[ $(segment_size) -ge 128 ]]; then \
		if [[ `expr $(segment_size) % 128` -eq 0 ]]; then \
			printf "Good segment_size %d\n" $(segment_size) ; \
		else \
			printf "Bad segment_size %d\n" $(segment_size) ; \
		fi ; \
	else \
		echo " Bad segment_size", $(segment_size) ; \
	fi ;

$(OUTPUT): $(OBJS) gf_complete.a
	ar rcs $@ $^
	$(CC) -shared -o librlc.so -fPIC $^
	ls -lrt $(OUTPUT) librlc.so

clean:
	-rm -f $(OBJS)
	-rm -rf $(OUTPUT)
