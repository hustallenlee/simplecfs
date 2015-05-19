#ifndef MAT_H
#define MAT_H
#include "galois.h"

#define mat_init(pmat)  \
        do{             \
            (pmat)->data = NULL;  \
            (pmat)->row  = 0;     \
            (pmat)->col  = 0;     \
        }while(0)

#define sizeofmat(row, col) ((row)*(col)*sizeof(gfele_t))

typedef struct{
    int row;
    int col;
    gfele_t * data;
} gfmat_t, *pgfmat_t;

int load(gfmat_t * pmat, char * filename);
int dump(gfmat_t * pmat, char * filename);

int check_matrix(gfmat_t * pmat);
int print_matrix(gfmat_t * pmat);

int resize_matrix(gfmat_t * pmat, int row, int col);

int set(gfmat_t *pmat, int x, int y, gfele_t ele);
int set_whole_row(gfmat_t *pmat, int row, gfele_t val);
int set_whole_col(gfmat_t *pmat, int col, gfele_t val);
int set_by_row(gfmat_t *pmat, int row, int start, int len, gfele_t val);
int set_by_col(gfmat_t *pmat, int col, int start, int len, gfele_t val);
gfele_t get(gfmat_t *pmat, int x, int y);
int make_from_array(gfmat_t * pmat, gfele_t * arr, int row, int col);
int make_empty(gfmat_t * pmat);
int make_zero(gfmat_t * pmat, int row, int col);
int make_identity(gfmat_t * pmat, int row, int col);
int make_random(gfmat_t * pmat, int row, int col, int max);
int make_rrandom(gfmat_t * pmat, int row, int col, gfele_t floor, gfele_t roof);

int make_vandermonde(gfmat_t * pmat, int n, int k, gfm_t *gf);
int make_sys_vandermonde(gfmat_t * pmat, int n, int k, gfm_t *gf);
int make_parity_vandermonde(gfmat_t * pmat, int m, int k, gfm_t *gf);
int make_sys_xvandermonde(gfmat_t *pmat, int n, int k, gfm_t *gf, int *list);
int make_parity_xvandermonde(gfmat_t *pmat, int m, int k, gfm_t *gf, int *list);
int make_cauchy(gfmat_t * pmat, int row, int col, gfm_t *gf);
int make_general_best_cauchy(gfmat_t* pmat, int row, int col, int w, gfm_t *gf);
int make_general_best_parity_cauchy(gfmat_t* pmat, int row, int col, int w, gfm_t *gf);
int make_sys_cauchy(gfmat_t * pmat, int row, int col, gfm_t *gf);
int make_parity_cauchy(gfmat_t * pmat, int row, int col, gfm_t *gf);

int make_RRS(gfmat_t * pmat, int k, int m, int r);
int make_LRC(gfmat_t * pmat, int k, int m, int ln, gfm_t *pgf); 

/*int make_parity_z_bitmatrix(gfmat_t *pmat, int n, int k);*/
//int make_parity_z_vandermonde(gfmat_t *pmat, int n, int k, gfm_t *gf);
//int make_parity_z_cauchy(gfmat_t *pmat, int n, int k, gfm_t *gf);

int mat_free(gfmat_t *mat);

int del_row(gfmat_t * pmat, int row);
int del_col(gfmat_t * pmat, int col);
int del_rows(gfmat_t * pmat, int begin, int len);
int del_cols(gfmat_t * pmat, int begin, int len);
int del_allzero_cols(gfmat_t *pmat);
int del_allzero_rows(gfmat_t *pmat);

int add_row(gfmat_t * pmat, int to, int from);
int add_irow(gfmat_t * pmat, int to, int from, gfele_t prod, gfm_t *gf);
int irow(gfmat_t * pmat, int row, gfele_t val, gfm_t *gf);

int transpose_matrix(gfmat_t * pmat);
int inverse_matrix(gfmat_t * pmat,  gfm_t *gf);

int copy_matrix(gfmat_t * pmat_to, gfmat_t * pmat_from);

int select_by_rows(gfmat_t * pmat_new, int *list, int num, gfmat_t *pmat_from);

int append_matrix(gfmat_t * pmat, gfmat_t * pmat_app);
int append_part_of_matrix(gfmat_t * pmat, gfmat_t * pmat_app, int start, int len);

int insert_matrix(gfmat_t * pmat, gfmat_t * pmat_inr, int pos_row);
int insert_part_of_matrix(gfmat_t * pmat, gfmat_t * pmat_inr, int start, int len);

int get_part_of_matrix(gfmat_t * pmat, gfmat_t * pmat_from, int start, int len);

int replace_matrix(gfmat_t * pmat, gfmat_t * pmat_rep, int start, int len);

int wipe_matrix(gfmat_t * pmat, int begin, int len, gfele_t value);

int prod(gfmat_t * pmat_res, gfmat_t * pmat1, gfmat_t * pmat2, gfm_t * gf);
int prod_p(gfmat_t * pmat_res, gfmat_t * pmat1, gfmat_t * pmat2, gfm_t *gf, int thread_num);

int transform_to_systematic(gfmat_t * pmat, gfm_t *gf);
int transform_to_bitmatrix(gfmat_t *pbmat, gfmat_t *pmat, gfm_t *gf, int word);

int select_nodes_of_vectors(gfmat_t *pdmat, gfmat_t *psmat, int *snl, int k);

#endif
