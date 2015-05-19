#ifndef RLCLIB_CODE_COMMON_H
#define RLCLIB_CODE_COMMON_H

#include <fcntl.h>
#include <unistd.h>
#include <unistd.h>

typedef struct{
    int len;
    int * plist;
} blist_t;

void log_message(const char *filename, int line, const char *function, const char *fmt, ...);
#define LOG     log_message
#define print_error(fmt, args...) LOG(__FILE__, __LINE__, __FUNCTION__, fmt, ##args)

void * rlc_alloc(const char *filename, int line, const char *function, int size);
#define ALLOC   rlc_alloc
#define zalloc(size) ALLOC(__FILE__, __LINE__, __FUNCTION__,size)

int math_pow(int exp, int index);

void randomize_region(unsigned char *ptr, size_t len);

#endif /* end of include guard */

