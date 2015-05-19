#ifndef FILE_OPERATIONS_H
#define FILE_OPERATIONS_H
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

//all the filename are the absolute path;

//bat files operations
int bat_write_bylist(const char *filename, int *files_idx_list, int file_nums, unsigned char *out_buff, unsigned long size_each_file);

int bat_write_bynums(const char *filename, int file_nums, unsigned char *out_buff, unsigned long size_each_file);

int bat_read(const char *filename, int *files_idx_list, int file_nums, unsigned char *in_buf, unsigned long size_each_file);

//single file operations
int read_single_file(const char *filename, unsigned long file_size, unsigned char *buffer);

int write_2single_file(const char *filename, unsigned long file_size, unsigned char *buffer);

unsigned long get_filesize(const char *filename);

int get_des_filename(char *des_filename, const char *des_filepath, const char *src_filename);

#endif
