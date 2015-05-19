#ifndef RLCLIB_CRS_H
#define RLCLIB_CRS_H

#include "mat.h"
#include "code_common.h"

typedef struct {
    gfm_t *pgf;
    gfmat_t *pmat;
    int n;
    int k;
    int packet_size;
} crs_info_t;;

typedef struct {
    int (*encode)(crs_info_t *pcrsi);
    int (*decode)(crs_info_t *pcrsi, blist_t *phelp);
    int (*repair)(crs_info_t *pcrsi, blist_t *phelp, blist_t *pgen);
} crsm_t;

typedef struct {
    crs_info_t *pcrsi;
    crsm_t *pcrsm;
} crs_coder_t;

/** init the cauchy reed solomen code information
 * @param crs, cauchy reed_solomen code struct, contain code information and methods,already alloc memory.
 * @param n, Number of data plus coding devices,(without n *=word)
 * @param k, Number of data devices(without k*=word)
 * @param word, Word size
 * @param packet_size coding packet element size
 */
int crs_init(crs_coder_t *crs, int n, int k, int word, int packet_size);

/** free memory alloc in crs_init.
 * @param crs cauchy reed_solomen code struct, contain code information and methods.
 */
int crs_free(crs_coder_t *crs);

int crs_encode(crs_info_t *pcrsi,                  /* input */
        const char *orig_data, int data_size,   /* input */
        char **encoded_data,                    /* output */
        char **encoded_parity, int *chunk_size); /* output */

int crs_decode(crs_info_t *pcrsi,
        char *available_data,                           /* input */
        int *data_list, int data_num, int chunk_len,    /* input */
        char **out_data);                               /* output */

int crs_repair(crs_info_t *pcrsi,
        char *available_data,                        /* input */
        int *data_list, int data_num, int chunk_len, /* input */
        int *repair_list, int repair_num,            /* input */
        char **out_data);                            /* output */

#endif
