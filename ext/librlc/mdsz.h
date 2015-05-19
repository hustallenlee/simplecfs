#ifndef RLCLIB_MDSZ_H
#define RLCLIB_MDSZ_H

#include "zcode_struct.h"

typedef struct {
    coomat_t *pcoomat; // only the parity matrix
    gfm_t   gf;
    int m;
    int k;
    char *des_filename;
    char *src_filename;
    int filesize;
    int packetsize;
    int blocksize;
} mdsz_info_t;

typedef struct {
    int (*encode)(mdsz_info_t *pmdszi);
    int (*decode)(mdsz_info_t *pmdszi);
    int (*repair)(mdsz_info_t *pmdszi, int node);
} mdszm_t;

typedef struct {
    mdsz_info_t *pmdszi;
    mdszm_t *pmdszm;
} mdsz_coder_t;

int mdsz_init(mdsz_coder_t *pmdsz, int m, int k, const char *des_filepath, const char *src_filename, int packetsize);

int mdsz_free(mdsz_coder_t *pz);

#endif // end of RLCLIB_MDSZ_H
