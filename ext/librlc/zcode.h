#ifndef RLCLIB_ZCODE_H
#define RLCLIB_ZCODE_H

#include "zcode_struct.h"

typedef struct {
    lil_t *pzlil; // only the parity mat 
    int m;
    int k;
    int packetsize;
} z_info_t;

typedef struct {
    int (*encode)(z_info_t *pzi);
    int (*decode)(z_info_t *pzi);
    int (*repair)(z_info_t *pzi, int node);
} zm_t;

typedef struct {
    z_info_t *pzi;
    zm_t *pzm;
} z_coder_t;

int z_init(z_coder_t *pz, int m, int k, int packetsize);

int z_free(z_coder_t *pz);

int z_encode(z_info_t *pzi,                  /* input */
        const char *orig_data, int data_size,   /* input */
        char **encoded_data,                    /* output */
        char **encoded_parity, int *chunk_size); /* output */

/* chunk list is a array of (n-1)*m^(k-2) */
int z_repair_chunk_needed(int m, int k, int node, /* input */
        int chunk_num, /* input */
        int *chunk_list);         /* output */

int z_repair(z_info_t *pzi,
        char *available_data,                        /* input */
        int *data_list, int data_num, int chunk_len, /* input */
        int node,                                   /* input */
        char **out_data);                            /* output */

#endif // end of RLCLIB_ZCODE_H

