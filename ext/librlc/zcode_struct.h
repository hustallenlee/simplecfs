#ifndef ZCODE_STRUCT_H
#define ZCODE_STRUCT_H

#include <stdint.h>
#include "code_common.h"
#include "mat.h"

#define ZLIL_R(m,k) (math_pow((m),(k-1)))
#define ZLIL_ROW(m,k) ((m)*(math_pow((m),(k-1))))
#define ZLIL_COL(m,k) (k)
#define ZLIL_DATA_ALLOC(m,k) ((gfele_t *)calloc(1, ZLIL_ROW((m),(k))*ZLIL_COL((m),(k))*sizeof(gfele_t)))

#define ZMAT_R(m,k) (math_pow((m),(k-1)))
#define ZMAT_ROW(m,k) ((m)*(math_pow((m),(k-1))))
#define ZMAT_COL(m,k) ((k)*(math_pow((m),(k-1))))
#define ZMAT_DATA_ALLOC(m,k) ((gfele_t *)calloc(1, ZMAT_ROW((m),(k))*ZMAT_COL((m),(k))*sizeof(gfele_t)))

typedef gfmat_t zmat_t;

typedef struct lil_t{
    int row;
    int col;
    int rawcol;
    gfele_t *data;
} lil_t;

typedef struct coomat_t{
    int type;
    lil_t lil_pos;
    gfmat_t mat_val;
} coomat_t;

// for zinverse

typedef struct _mat_node {
    int pos;
    gfele_t value;
    struct _mat_node *pnext;
}mat_node;

typedef struct  _head {
    int len;
    mat_node *phead;
}head_t;

int inverse_coomat(coomat_t *pcoomat, gfm_t *gf);
int inverse_gfmat(gfmat_t *pgmat, gfm_t *gf);
int inverse_lil(lil_t *pzlil, gfm_t *gf);

/*
 *     Z code      --->  lil_t(zmat_t)
 * MDS Z code      --->  coomat_t(zmat_t)
 *     Z-LIL code  --->  lil_t
 * MDS Z-LIL code  --->  coomat_t
 *
 */

int make_z_coomat(coomat_t *pzcoomat, zmat_t *pmat, int m, int k);
int make_z_lil(lil_t *pzlil, int m, int k);
int make_z_mat(zmat_t *pzmat, int m, int k);
int make_zg_mat(zmat_t *pzmat, gfmat_t *pmat, int m, int k);

/*int init_zmat(zmat_t *pzmat, int m, int k);*/
/*int init_zlil(lil_t *pzlil, int m, int k);*/
/*int lil_k2(lil_t *pzlil, int m);*/
/*int mat_k2(zmat_t *pzmat, int m);*/
/*int lil_ins_k(lil_t *pl_new, lil_t *pl_ori, int m, int k);*/
/*int mat_ins_k(zmat_t *pm_new, zmat_t *pm_ori, int m, int k);*/

void zlil_free(lil_t *pzlil);
void zcoomat_free(coomat_t *pzcoomat);

int **get_repair_list(int m, int k, int fnode);
void print_repair_list(int **list, int m, int k);

void print_lil(lil_t *pzlil);
void print_zmat_bit(zmat_t *pzmat, int m);
int  print_coomat(coomat_t * pzcoomat);

void dump_lil(lil_t *pzlil, int m, int k, char *filename);
void dump_gfmat(zmat_t *pzmat,  int m, int k, char *filename);

void extend_to_systematic_coomat(coomat_t *pcmat, int m, int k);
/* only for Z codes/MDS Z codes */
int zmat_to_lil(lil_t *pzlil, zmat_t *pzmat);
int lil_to_zmat(zmat_t *pzmat, lil_t *pzlil);
int zmat_to_coomat(coomat_t *pzcoomat, zmat_t *pzmat);
int coomat_to_zmat(zmat_t *pzmat, coomat_t *pzcoomat);

#endif
