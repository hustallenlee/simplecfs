#ifndef RLCLIB_RS_H
#define RLCLIB_RS_H

#include "mat.h"
#include "code_common.h"

typedef struct{
    gfm_t *pgf;
    gfmat_t *pmat;
    int n;
    int k;
    int packet_size;
} rs_info_t;

typedef struct{
    int (*encode)(rs_info_t *prsi);
    int (*decode)(rs_info_t *prsi, blist_t *phelp);
    int (*repair)(rs_info_t *prsi, blist_t *phelp, blist_t *pgen);
} rsm_t;

typedef struct{
    rs_info_t * prsi;
    rsm_t *prsm;
} rs_coder_t;

/** init the reed solomen code information
 * @param rs reed_solomen code struct, contain code information and methods,already alloc memory.
 * @param n Number of data plus coding devices
 * @param k Number of data devices
 * @param word Word size,value 8/16/32
 * @param packet_size coding packet element size
 * @param data_size encode original data size 
 */
int rs_init(rs_coder_t *rs, int n, int k, int word, int packet_size);

/** free memory alloc in rs_init.
 * @param rs reed_solomen code struct, contain code information and methods.
 */
int rs_free(rs_coder_t *rs);

/** encode and store to separate files
 * @param prsi, rs information,
 * @param orig_data, data to be encoded
 * @param data_len, orig data len
 * @param encoded_data, data after encoded, store in an array of k*chunk_size
 * @param encoded_parity, parity data , store in and array of m*chunk_size
 * @param chunk_size, store the chunk size, data and parity are k+m chunk
 *
 * return 0 in case of error, otherwise return 1;
 * caller should free the encoded_data, encoded_parity
 */
int rs_encode(rs_info_t *prsi,                  /* input */
        const char *orig_data, int data_size,   /* input */
        char **encoded_data,                    /* output */
        char **encoded_parity, int *chunk_size); /* output */

/**
 * Reconstruct original data from a set of k encoded chunk
 *
 * @param prsi- rs information
 * @param available_data - erasure encoded chunk (k*chunk_len)
 * @param data_list - number of fragments being passed in(>=k)
 * @param data_num - num of data chunk for decode (>=k)
 * @param chunk_len - length of each chunk(assume they are the same)
 * @param out_data - _output_ pointer to decoded data
 *          (output data pointers are allocated by librlc,
 *           caller invokes librlc_decode_clean() after it has
 *           read decoded data in 'out_data')
 *
 * @return 0 on success, -error code otherwise
 */
int rs_decode(rs_info_t *prsi,
        char *available_data,                           /* input */
        int *data_list, int data_num, int chunk_len,    /* input */
        char **out_data);                               /* output */

/**
 * Reconstruct  missing fragments from a subset of available fragments
 *
 * @param prsi - rs information
 * @param available_data- erasure encoded chunks 
 * @param data_num - number of chunks being passed in
 * @param chunk_len - size in bytes of the chunk
 * @param repair_list - missing chunks' index to reconstruct
 * @param repair_num - missing chunks' num to reconstruct
 * @param out_data - output of reconstruct
 *
 * @return 0 on success, -error code otherwise
 */
int rs_repair(rs_info_t *prsi,
        char *available_data,                        /* input */
        int *data_list, int data_num, int chunk_len, /* input */
        int *repair_list, int repair_num,            /* input */
        char **out_data);                            /* output */

#endif /* end of include guard */
