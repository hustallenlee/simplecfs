#ifndef GFSHIFT_H
#define GFSHIFT_H
#include<nmmintrin.h>
#include<emmintrin.h>

#include "galois.h"
#include "region_xor.h"

typedef struct gfshift{
    gfele_t (*mul)(gfele_t a, gfele_t b);
    gfele_t (*div)(gfele_t a, gfele_t b);
    gfele_t (*inv)(gfele_t a);
    int (*region_mul)(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
    int (*region_mul2)(gfele_t *region, int len);
} gfs_t;

int region_mul_2_64_w4(gfele_t *region, int len);
int region_mul_2_64_w8(gfele_t *region, int len);
int region_mul_2_64_w16(gfele_t *region, int len);
int region_mul_2_64_w32(gfele_t *region, int len);

int region_shift_mul_w4(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_shift_mul_w8(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_shift_mul_w16(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_shift_mul_w32(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_mul_2_w16_sse(gfele_t *des, gfele_t *src, int len, int ifxor);
int region_mul_2_w32_sse(gfele_t *des, gfele_t *src, int len, int ifxor);

int gfs_init(gfs_t * gfs, int w);
#endif
