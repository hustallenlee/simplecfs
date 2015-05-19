#ifndef GALOIS_H
#define GALOIS_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

typedef uint32_t gfele_t;

typedef struct{
    gfele_t (*mul)(gfele_t a, gfele_t b);
    gfele_t (*div)(gfele_t a, gfele_t b);
    gfele_t (*inv)(gfele_t a);
    int (*region_mul)(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
} gfm_t;

int gf_init(gfm_t * gf, int w);
int gf_free();

//create basic tables
gfele_t galois_create_log_tables(int ww);
gfele_t galois_create_mult_tables(int ww);
gfele_t galois_create_split_w8_tables();


//mul, div and inverse operations for multi_table, namely w = 1 ~ 9
gfele_t single_mul_t(gfele_t a, gfele_t b);
gfele_t single_div_t(gfele_t a, gfele_t b);
gfele_t single_inv_t(gfele_t a);

//operations for log tables, namely w = 10 ~ 22
gfele_t single_mul_l(gfele_t a, gfele_t b);
gfele_t single_div_l(gfele_t a, gfele_t b);
gfele_t single_inv_l(gfele_t a);

//operations for shift, when w = 23 ~ 31
gfele_t single_mul_s(gfele_t a, gfele_t b);
gfele_t single_div_s(gfele_t a, gfele_t b);
gfele_t single_inv_s(gfele_t a);

//especially w = 32, the operations. what's more, here's inverse operation is same to the single_inv_s() func
gfele_t single_mul_split(gfele_t a, gfele_t b);
gfele_t single_div_split(gfele_t a, gfele_t b);


gfele_t split_table_w8_multiply(gfele_t x, gfele_t y);
gfele_t galois_shift_multiply(gfele_t x, gfele_t y);


gfele_t galois_shift_inverse(gfele_t x);

//by such two func, we can get the log and ilog tables' value easily
gfele_t galois_log(gfele_t value);
gfele_t galois_ilog(gfele_t value);


// region_mul for Table, Log table, shiFt respectively
int region_mul_wt(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_mul_wl(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_mul_wf(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);

int region_mul_w8(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_mul_w16(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);
int region_mul_w32(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor);

int region_mul_2_w8(gfele_t *des, gfele_t *src, int len, int ifxor);
int region_mul_2_w16(gfele_t *des, gfele_t *src, int len, int ifxor);
int region_mul_2_w32(gfele_t *des, gfele_t *src, int len, int ifxor);

#endif
