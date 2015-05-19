#include <sys/stat.h>
#include "file_operations.h"

//this func we can choose the idx_list, not in the ascending order
int bat_write_bylist(const char *filename, int files_idx_list[], int file_nums, unsigned char *out_buff, unsigned long size_each_file) {
    FILE *fp;
    int i;
    //char t_filename[256];
    char each_filename[128];
    unsigned char *p_f_buff = out_buff;

    //strcpy(t_filename, filepath);
    //strcat(t_filename, filename);

    for(i = 0; i < file_nums; ++i) {
        sprintf(each_filename, "%s%c%02d", filename, '_', files_idx_list[i]);
        if(NULL == (fp = fopen(each_filename, "w"))) {
            fprintf(stderr, "cannot create the file %s\n", each_filename);
            return 0;
        }
        p_f_buff = out_buff;
        p_f_buff = p_f_buff + i * size_each_file;
        fwrite(p_f_buff, size_each_file, 1, fp);
        fclose(fp);
    }
    return 1;
}

int bat_write_bynums(const char *filename, int file_nums, unsigned char *out_buff, unsigned long size_each_file) {
    FILE *fp;
    int i;
    //char t_filename[256];
    char each_filename[128];
    unsigned char *p_f_buff;

    //strcpy(t_filename, filepath);
    //strcat(t_filename, filename);

    for(i = 0; i < file_nums; ++i) {
        sprintf(each_filename, "%s%c%02d", filename, '_', i);
        if(NULL == (fp = fopen(each_filename, "w"))) {
            fprintf(stderr, "can not create file %s\n", each_filename);
            return 0;
        }
        p_f_buff = out_buff;
        p_f_buff = p_f_buff + i * size_each_file;
        fwrite(p_f_buff, size_each_file, 1, fp);
        fclose(fp);
    }
    
    return 1;
}

int bat_read(const char *filename, int file_idx_list[], int file_nums, unsigned char *in_buff, unsigned long size_each_file) {
    FILE *fp;
    int i;
    //char t_filename[256];
    char each_filename[128];

    //strcpy(t_filename, filepath);
    //strcat(t_filename, filename);
    
    for(i = 0; i < file_nums; ++i) {
        sprintf(each_filename, "%s%c%02d", filename, '_', file_idx_list[i]);
        if(NULL == (fp = fopen(each_filename, "r"))) {
            fprintf(stderr, "not found file %s\n", each_filename);
            return 0;
        }
        if(0 == fread(in_buff + i * size_each_file, size_each_file, 1, fp)) {
            fprintf(stderr, "fread error, and the return value is 0, file name is %s\n", each_filename);
            return 0;
        }
        fclose(fp);
    }

    return 1;
}

int read_single_file(const char *filename, unsigned long file_size, unsigned char *buffer) {
    FILE *fp;
    //unsigned long len;

    if(NULL == (fp = fopen(filename, "r"))) {
        fprintf(stderr, "not found file %s\n", filename);
        return 0;
    }
    
    if(0 == fread(buffer, file_size, 1, fp)) {
        fprintf(stderr, "fread error, and the return value is 0\n");
        return 0;
    }
    fclose(fp);

    return 1;
}

int write_2single_file(const char *filename, unsigned long file_size, unsigned char *buffer) {
    FILE *fp;

    if(NULL == (fp = fopen(filename, "w"))) {
        fprintf(stderr, "can not create file %s\n", filename);
        return 0;
    }

    fwrite(buffer, file_size, 1, fp);
    fclose(fp);

    return 1;
}

unsigned long get_filesize(const char *filename) {
    struct stat fstat;
    if(-1 == stat(filename, &fstat)) {
        fprintf(stderr, "stat reading error in func get_filesize()\n");
        return 0;
    }
    return fstat.st_size;
}

int get_des_filename(char *des_filename, const char *des_filepath, const char *src_filename) {
    char *p, *path;
    char *position;
    int l;

    p = (char *) malloc (sizeof(char) * strlen(src_filename));
    path = p;

    strcpy(path, src_filename);
    
    position = strstr(path, "/");

    do {
        l = strlen(position) + 1;
        path = &path[strlen(path) - l + 2];
        position = strstr(path, "/");
    } while(position);


    strcpy(des_filename, des_filepath);
    strcat(des_filename, path);
    //printf("%s\n", des_filename);

    free(p);
    return 1;
}
