#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <pthread.h>
#include <string.h>

#include "mat.h"
#include "zcode_struct.h"
#include "best_cauchy.h"
#include "region_xor.h"

int load(gfmat_t * pmat, char * filename){
    int row = 0, col = 0;
    int i, j;
    FILE *fp;
    unsigned int ele;


    if(!(fp = fopen(filename, "r"))){
        printf("Error : cann't open the file: %s\n", filename);
        exit(-1);
    }
    if(0 == fscanf(fp, "row:%d\n", &row)){
        printf("Error : Broken file!(bad row)\n");
        return 0;
    }
    if(0 == fscanf(fp, "col:%d\n", &col)){
        printf("Error : Broken file!(bad col)\n");
        return 0;
    }
    
    pmat->row = row;
    pmat->col = col;
    if(pmat->data != NULL){
        pmat->data = (gfele_t *)realloc(pmat->data, sizeofmat(row, col));
    }else{
        pmat->data = (gfele_t *)malloc(sizeofmat(row, col));
    }
    
    for(i = 0; i < row; ++i){
        for(j = 0; j < col; ++j){
            if(EOF == fscanf(fp, "%u", &ele)){
                printf("Broken file!(at(i, j))\n");
                free(pmat->data);
                return 0;
            }
            pmat->data[i*col+j] = (gfele_t)ele;
        }
    }

    fclose(fp);

    return row;
}

int dump(gfmat_t * pmat, char * filename){
    int row = 0, col = 0;
    int i, j;
    FILE *fp;
    
    if(!(fp = fopen(filename, "w+"))){
        printf("cann't open the file: %s\n", filename);
        exit(-1);
    }

    row = pmat->row;
    col = pmat->col;

    fprintf(fp, "row:%d\n", row);
    fprintf(fp, "col:%d\n", row);

    for(i = 0; i < row; ++i){
        for(j = 0; j < col; ++j){
            fprintf(fp, "%u\t", pmat->data[i*col+j]);
        }
        fprintf(fp, "\n");
    }

    fclose(fp);

    return row;
}

int resize_matrix(gfmat_t * pmat, int row, int col){
    
    assert(pmat != NULL);

    if((row == 0)||(col == 0)){
        pmat->row = 0;
        pmat->col = 0;
        pmat->data = NULL;
        
        return 0;
    }

    if(pmat->data == NULL){
        if((pmat->data = (gfele_t *)malloc(sizeofmat((size_t)row, col))) == NULL){
            printf("ERROR: Fail to alloc mem for the matrix!\n");
            return 0;
        }
    }else{
        if((pmat->row)*(pmat->col) != row*col){
            if((pmat->data = (gfele_t *)realloc(pmat->data, sizeofmat((size_t)row, col))) == NULL){
                printf("ERROR: Fail to alloc mem for the matrix!\n");
                return 0;
            }
        }
    }

    pmat->row = row;
    pmat->col = col;

    return row;
}

int set(gfmat_t *pmat, int x, int y, gfele_t ele){
    int col = pmat->col;

    pmat->data[x*col+y] = ele;

    return ele;
}

gfele_t get(gfmat_t *pmat, int x, int y){
    int col = pmat->col;

    return pmat->data[x*col+y];
}

int set_whole_row(gfmat_t *pmat, int row_index, gfele_t val){
    gfele_t *ptr;
    int col = pmat->col;
    int i;

    ptr = pmat->data+row_index*col;
    for(i = 0; i < col; ++i){
        (*ptr) = val;
        ++ptr;
    }

    return 0;
}

int set_whole_col(gfmat_t *pmat, int col_index, gfele_t val){
    gfele_t *ptr;
    int row = pmat->row;
    int i;

    ptr = pmat->data+col_index;
    for(i = 0; i < row; ++i){
        (*ptr) = val;
        ptr = ptr + row;
    }

    return 0;
}

int set_by_row(gfmat_t *pmat, int row_index, int start, int len, gfele_t val){
    gfele_t *ptr;
    int col = pmat->col;
    int i;

    if(start+len > col){
        printf("ERROR: length overflow!\n");
        return 0;
    }

    ptr = pmat->data+row_index*col+start;
    for(i = 0; i < len; ++i){
        (*ptr) = val;
        ++ptr;
    }

    return 0;
}

int set_by_col(gfmat_t *pmat, int col_index, int start, int len, gfele_t val){
    gfele_t *ptr;
    int row = pmat->row;
    int i;
    
    if(start+len > row){
        printf("ERROR: length overflow!\n");
        return 0;
    }

    ptr = pmat->data+start*row+col_index;
    for(i = 0; i < len; ++i){
        (*ptr) = val;
        ptr = ptr + row;
    }

    return 0;
}

int make_from_array(gfmat_t * pmat, gfele_t * arr, int row, int col){
    
    resize_matrix(pmat, row, col);
    memcpy(pmat->data, arr, sizeofmat(row, col));

    return row;
}

int make_empty(gfmat_t * pmat){
    pmat->row = 0;
    pmat->col = 0;
    
    if(pmat->data != NULL){
        free(pmat->data);
    }
    pmat->data = NULL;

    return 0;
}

int make_zero(gfmat_t * pmat, int row, int col){
    size_t len;

    resize_matrix(pmat, row, col);
    len = ((size_t)row)*((size_t)col)*sizeof(gfele_t);
    memset(pmat->data, 0, len);

    return pmat->row;
}

int make_identity(gfmat_t * pmat, int row, int col){
    int i;

    assert(row == col);
    assert(row > 0);
    make_zero(pmat, row, col);
    
    for(i = 0; i < row; i++){
        pmat->data[i*col+i] = 1;
    }

    return pmat->row;
}

int make_random(gfmat_t * pmat, int row, int col, int max){
    int i;
    gfele_t *pmdata;

    assert(max > 0);

    resize_matrix(pmat, row, col);
    pmdata = pmat->data;

    for(i = 0; i < row*col; ++i){
        (*pmdata) = (gfele_t)rand()%max;
        ++pmdata;
    }

    return pmat->row;
}

int make_rrandom(gfmat_t * pmat, int row, int col, gfele_t floor, gfele_t roof){
    int i;
    gfele_t *pmdata;

    assert(floor > 0);
    assert(roof > floor);

    resize_matrix(pmat, row, col);

    pmdata = pmat->data;

    for(i = 0; i < row*col; ++i){
        (*pmdata) = rand()%(roof-floor) + floor;
        ++pmdata;
    }

    return pmat->row;
}

int make_vandermonde(gfmat_t * pmat, int row, int col, gfm_t *gf){
    int i, j;
    gfele_t *pmdata;
    gfele_t val;

    resize_matrix(pmat, row, col);
    pmdata = pmat->data;
    
    pmdata[0] = 1;
    memset(pmdata+1, 0, (col-1)*sizeof(gfele_t));

    for(i = 1; i < row; ++i){
        val = 1;
        for(j = 0; j < col; ++j){
            pmdata[i*col+j] = val;
            val = gf->mul(val, i);
        }   
    }

    return pmat->row;
}

int make_sys_vandermonde(gfmat_t * pmat, int n, int k, gfm_t *gf){
    
    assert(n >= k);
    resize_matrix(pmat, n, k);
    make_vandermonde(pmat, n, k, gf);
    transform_to_systematic(pmat, gf);

    return pmat->row;
}

int make_parity_vandermonde(gfmat_t * pmat, int m, int k, gfm_t *gf){

    assert(m > 0);

    make_sys_vandermonde(pmat, m+k, k, gf);
    del_rows(pmat, 0, k);

    return pmat->row;
}

int make_sys_xvandermonde(gfmat_t *pmat, int row, int col, gfm_t *gf, int *list){
    int i, j;
    gfele_t val;
    gfele_t *pmdata;
    
    resize_matrix(pmat, row, col);
    pmdata = pmat->data;

    for(i = 0; i <row; ++i){
        val = 1;
        for(j = 0; j < col; ++j){
            pmdata[i*col+j] = val;
            val = gf->mul(val, (list[i]));
        }
    }
    
    transform_to_systematic(pmat, gf);
    return pmat->row;
}

int make_parity_xvandermonde(gfmat_t *pmat, int row, int col, gfm_t *gf, int *list){
    make_sys_xvandermonde(pmat, row+col, col, gf, list);
    del_rows(pmat, 0, col);

    return row;
}


int make_general_best_cauchy(gfmat_t * pmat, int n, int k, int w, gfm_t *gf){

    resize_matrix(pmat, n, k);
    
    cauchy_good_general_coding_matrix(pmat, k, n, w, gf);

    return pmat->row;
}

int make_general_best_parity_cauchy(gfmat_t* pmat, int m, int k, int w, gfm_t *gf){

    resize_matrix(pmat, m, k);
    
    cauchy_good_general_coding_matrix(pmat, k, m, w, gf);
    transform_to_systematic(pmat, gf);
    del_rows(pmat, 0, k);

    return pmat->row;
}

int make_cauchy(gfmat_t * pmat, int m, int k, gfm_t *gf){
    int i, j;
    gfele_t *pmdata;

    resize_matrix(pmat, m, k);
    pmdata = pmat->data;
    
    for(i = 0; i < m; ++i){
        for(j = 0; j < k; ++j){
            pmdata[i*k+j] = gf->div(1, (i^(m+j)));
        }
    }

    return pmat->row;
}

int make_sys_cauchy(gfmat_t * pmat, int n, int k, gfm_t *gf){
    gfmat_t mat_p;

    assert(n >= k);

    mat_init(&mat_p);
    make_identity(pmat, k, k);
    make_cauchy(&mat_p, n-k, k, gf);
    append_matrix(pmat, &mat_p);

    mat_free(&mat_p);
    return pmat->row;
}

int make_parity_cauchy(gfmat_t * pmat, int row, int col, gfm_t *gf){
    make_cauchy(pmat, row-col, col, gf);
    return pmat->row;
}

/***************** specific matrix *************************/

gfele_t power2(int power){
    int i;
    gfele_t res = 1;

    for(i = 0; i < power; ++i){
        res = single_mul_t((gfele_t)res, (gfele_t)2);
    }

    return res;
}

int make_RRS(gfmat_t * pmat, int k, int m, int r){
    int row, col;
    int ii, ij, ia;
    int border;

    row = r*m;
    col = r*k;
    
    make_zero(pmat, row, col);
    for(ii = 0; ii < m; ++ii){
        border = k*ii/m;
        for(ij = 0; ij < r; ++ij){
            for(ia = 0; ia < k; ++ia){
                if(ia < border){
                    set(pmat, ii*r+ij, ia*r+(ij+1)%r, power2(ii+ij));
                }else{
                    set(pmat, ii*r+ij, ia*r+ij, power2(ii+ij));
                }
            }
        }
    }
    
    return 0;
}

int make_LRC(gfmat_t * pmat, int k, int m, int ln, gfm_t *pgf){ //m: total parity number, ln: data blocks in a group
    int global_m = m-k/ln;
    int group_num = k/ln;
    int i;
    gfmat_t matv;

    if(k%ln != 0){
        printf("the number of all data blocks in a group(k) must be exactly divided by the number of data blocks in a group(ln)\n");
        return 0;
    }

    mat_init(&matv);

    make_zero(pmat, group_num, k);
    for(i = 0; i < group_num; ++i){
        set_by_row(pmat, i, i*ln, ln, 1);
    }

    make_parity_vandermonde(&matv, global_m, k, pgf);
    append_matrix(pmat, &matv);

    mat_free(&matv);
    return 0;
}

/***************** specific matrix *************************/


/*int make_parity_z_bitmatrix(gfmat_t *pmat, int n, int k){*/
    /*int m, ki;*/
    /*int *pm1, *pm2;*/

    /*assert(sizeof(gfele_t) == sizeof(int));*/

    /*m = n-k;*/
    /*pm1 = NULL;*/
    /*pm2 = NULL;*/

    /*if((m > 4)||(m < 2)){*/
        /*printf("Error: m must be one of 2/3/4\n");*/
        /*return 0;*/
    /*}*/
    
    /*resize_matrix(pmat, ZMAT_ROW(m, k), ZMAT_COL(m, k));*/

    /*ki = 2;*/
    /*pm1 = (int *)Z_CALLOC(m, k);*/
    /*init_k2(pm1, m);*/

    /*if(k > 2){*/
        /*for(ki = 3; ki <= k; ++ki){*/
            /*pm2 = (int *)Z_CALLOC(m, ki);*/
            /*ins_k(pm2, pm1, m, ki-1);*/
            /*free(pm1);*/
            /*pm1 = (int *)Z_CALLOC(m, ki);*/
            /*memcpy(pm1, pm2, ZMAT_ROW(m, ki)*ZMAT_COL(m, ki)*sizeof(int));*/
        /*}*/
        /*memcpy(pmat->data, (gfele_t *)pm2, ZMAT_ROW(m, k)*ZMAT_COL(m, k)*sizeof(int));*/
    /*}else{*/
        /*memcpy(pmat->data, (gfele_t *)pm1, ZMAT_ROW(m, k)*ZMAT_COL(m, k)*sizeof(int));*/
    /*}*/
    /*free(pm1);*/
    /*if(pm2 != NULL){*/
        /*free(pm2);*/
    /*}*/

    /*return 1;*/
/*}*/

/*int make_parity_z_vandermonde(gfmat_t *pmat, int n, int k, gfm_t *gf){*/
    /*int i, j, p, q;*/
    /*int m;*/
    /*int block_size;*/
    /*gfmat_t mat;*/

    /*mat_init(&mat);*/
    /*m = n - k;*/
    /*make_parity_vandermonde(&mat, m, k, gf);*/
    /*make_parity_z_bitmatrix(pmat, n, k);*/
    
    /*block_size = Z_BLOCK(m, k);*/
    /*for(i = 0; i < m*block_size; ++i){*/
        /*for(j = 0; j < k*block_size; ++j){*/
            /*if(pmat->data[i*k*block_size+j] == 0)continue;*/
            /*p = i/block_size;*/
            /*q = j/block_size;*/
            /*pmat->data[i*k*block_size+j] = (gfele_t)mat.data[p*k+q];*/
        /*}*/
    /*}*/

    /*mat_free(&mat);*/
    /*return 1;*/
/*}*/

/*int make_parity_z_cauchy(gfmat_t *pmat, int n, int k, gfm_t *gf){*/
    /*int i, j, p, q;*/
    /*int m;*/
    /*int block_size;*/
    /*gfmat_t mat;*/

    /*mat_init(&mat);*/
    /*m = n - k;*/
    /*make_cauchy(&mat, n, k, gf);*/
    /*make_parity_z_bitmatrix(pmat, n, k);*/
    
    /*block_size = Z_BLOCK(m, k);*/
    /*for(i = 0; i < m*block_size; ++i){*/
        /*for(j = 0; j < k*block_size; ++j){*/
            /*if(pmat->data[i*k*block_size+j] == 0)continue;*/
            /*p = i/block_size;*/
            /*q = j/block_size;*/
            /*pmat->data[i*k*block_size+j] = (gfele_t)mat.data[p*k+q];*/
        /*}*/
    /*}*/

    /*mat_free(&mat);*/
    /*return 1;*/
/*}*/

int check_matrix(gfmat_t * pmat){

    printf("CHECK: row = %d, col = %d\n", pmat->row, pmat->col);
    if((pmat->row <= 0)||(pmat->col <= 0)){
        exit(-1);
    }
    if(pmat->data == NULL){
        printf("CHECK: matrix pointer is NULL\n");
    }

    return pmat->row;
}

int print_matrix(gfmat_t * pmat){
    int i, j;

    if(pmat->data == NULL){
        printf(" Null matrix\n");
        return 0;
    }
    assert(pmat->row > 0);
    assert(pmat->col > 0);

    for(i = 0; i < pmat->row; ++i){
        for(j = 0; j < pmat->col; ++j){
            printf("%x\t", pmat->data[i*(pmat->col)+j]);
        }
        printf("\n");
    }

    return pmat->row;
}

int mat_free(gfmat_t *mat){
    if(mat->data != NULL){
        free(mat->data);
        mat->data = NULL;
    }
    mat->row = 0;
    mat->col = 0;

    return 1;
}

int del_row(gfmat_t * pmat, int drow){
    gfele_t *p1;
    gfele_t *p2;
    int mov_size;

    assert(pmat->data != NULL);
    assert(drow >= 0);
    assert(drow < pmat->row);

    mov_size = (pmat->row - drow-1)*(pmat->col)*sizeof(gfele_t);
    p1 = pmat->data+drow*(pmat->col); 
    p2 = pmat->data+(drow+1)*(pmat->col);
    memmove(p1, p2, mov_size);

    pmat->row = pmat->row-1;
    pmat->data = (gfele_t *)realloc(pmat->data, ((pmat->row)*(pmat->col))*sizeof(gfele_t));

    return pmat->row;
}

int del_col(gfmat_t * pmat, int dcol){
    gfele_t *p2;
    int row, col;
    int i;

    assert(pmat->data != NULL);
    assert(dcol >= 0);
    assert(dcol < pmat->col);

    row = pmat->row;
    col = pmat->col;
    p2 = pmat->data;

    p2 = p2+dcol;

    for(i = 0; i < (row-1); ++i){
        memmove(p2, &(pmat->data[i*col+dcol+1]), (col-1)*sizeof(gfele_t));
        p2 = p2+col-1;
    }

    if(dcol < col-1){
        memmove(p2, &(pmat->data[(row-1)*col+dcol+1]), (col-dcol-1)*sizeof(gfele_t));
    }
    
    resize_matrix(pmat, pmat->row, pmat->col-1);
    
    return pmat->row;
}

int del_rows(gfmat_t * pmat, int begin, int len){
    gfele_t *p1;
    gfele_t *p2;
    int mov_size;

    assert(pmat != NULL);
    assert(begin >= 0);
    assert(begin+len <= pmat->row);

    mov_size = (pmat->row - begin-len)*(pmat->col)*sizeof(gfele_t);
    p1 = pmat->data+begin*(pmat->col); 
    p2 = pmat->data+(begin+len)*(pmat->col);
    memmove(p1, p2, mov_size);

    pmat->row  = pmat->row-len;
    pmat->data = (gfele_t *)realloc(pmat->data, ((pmat->row)*pmat->col)*sizeof(gfele_t));

    return pmat->row;
}

int del_cols(gfmat_t * pmat, int begin, int len){
    gfele_t *p1;
    gfele_t *p2;
    int row, col;
    int i;

    assert(pmat->data != NULL);
    assert(begin >= 0);
    assert(begin+len <= pmat->col);

    row = pmat->row;
    col = pmat->col;
    p1 = (gfele_t *)malloc(row*(col-len)*sizeof(gfele_t));
    p2 = p1;

    if(begin > 0){
        memcpy(p2, pmat->data, begin*sizeof(gfele_t));
        p2 = p2+begin;
    }

    for(i = 0; i < (row-1); ++i){
        memcpy(p2, &(pmat->data[i*row+begin+len]), (col-len)*sizeof(gfele_t));
        p2 = p2+col-len;
    }

    if(begin < col-1){
        memcpy(p2, &(pmat->data[(row-1)*col+begin+len]), (col-begin-len)*sizeof(gfele_t));
    }
    
    pmat->col -= len;
    
    pmat->data = (gfele_t *)realloc(pmat->data, (pmat->row)*(pmat->col)*sizeof(gfele_t));
    memcpy(pmat->data, p1, (pmat->row)*(pmat->col)*sizeof(gfele_t));
    free(p1);

    return pmat->row;
}

int del_allzero_cols(gfmat_t *pmat){
    int row = pmat->row;
    int col = pmat->col;
    int i,j;
    int num = 0;

    for(i = col-1; i >= 0; --i){
        for(j = 0; j < row; ++j){
            if(pmat->data[j*col+i] != 0){
                break;
            }
            if(j == row-1){
                del_col(pmat, i);
                col--;
                num++;
            }
        }
    } 
    
    return num;
}

int del_allzero_rows(gfmat_t *pmat){
    int row = pmat->row;
    int col = pmat->col;
    int i,j;
    int num = 0;

    for(i = row-1; i >= 0; --i){
        if((i%100) == 0)printf("%d\t", i);
        for(j = 0; j < col; ++j){
            if(pmat->data[i*col+j] != 0){
                break;
            }
            if(j == col-1){
                del_row(pmat, i);
                row--;
                --i;
                num++;
            }
        }
    } 
    
    return num;
}

int add_row(gfmat_t * pmat, int to, int from){
    int col;

    assert(pmat->data != NULL);
    assert(from >= 0);
    assert(to >= 0);
    assert(from < pmat->row);
    assert(to < pmat->row);

    col = pmat->col;
    region_xor_8(&(pmat->data[to*col]), &(pmat->data[from*col]), col*sizeof(gfele_t));

    return pmat->row;
}

int add_irow(gfmat_t * pmat, int to, int from, gfele_t prod, gfm_t *gf){
    int col;
    gfele_t *pmdata;

    assert(pmat->data != NULL);
    assert(from >= 0);
    assert(to >= 0);
    assert(from < pmat->row);
    assert(to < pmat->row);

    col = pmat->col;
    pmdata = pmat->data;
    
    gf->region_mul(&(pmdata[to*col]), &(pmdata[from*col]), prod, col*sizeof(gfele_t), 1);
    //for(i = 0; i < col; ++i){
    //    pmdata[to*col+i] ^= gf->mul(pmdata[from*col+i], prod);
    //}
    
    return pmat->row;
}

int irow(gfmat_t * pmat, int row, gfele_t val, gfm_t *gf){
    int i;
    int col;
    gfele_t *pmdata;

    assert(pmat->data != NULL);
    assert(row < pmat->row);

    col = pmat->col;
    pmdata = pmat->data;

    for(i = 0; i < col; ++i){
        pmdata[row*col+i] = gf->mul(pmdata[row*col+i], val);
    }
    
    return pmat->row;
}


int transpose_matrix(gfmat_t * pmat){
    int i, j;
    int row, col;
    int row_t, col_t;
    gfele_t * ptmm;

    assert(pmat->data != NULL);

    row = pmat->row;
    col_t = row;
    col = pmat->col;
    row_t = col;

    ptmm = (gfele_t *)malloc(row_t*col_t*sizeof(gfele_t));
    for(i = 0; i < row_t; ++i){
        for(j = 0; j < col_t; ++j){
            ptmm[i*col_t + j] = pmat->data[j*col+i];
        }  
    }

    memcpy(pmat->data, ptmm, row_t*col_t*sizeof(gfele_t));
    pmat->row = row_t;
    pmat->col = col_t;

    free(ptmm);

    return pmat->row;
}

int inverse_matrix(gfmat_t * pmat, gfm_t *gf){
    gfmat_t minv;
    gfele_t *pmdata;
    gfele_t *porig;
    gfele_t val;
    int dim;
    int i, j;
    int row_to_try;
    int data_size;

    assert(pmat->data != NULL);
    assert(pmat->row = pmat->col);

    dim = pmat->row;
    pmdata = pmat->data;
    mat_init(&minv);
    make_identity(&minv, dim, dim);

    data_size = dim*dim*sizeof(gfele_t);
    porig = (gfele_t *)malloc(data_size);
    memcpy(porig, pmat->data, data_size);

    for(i = 0; i < dim; ++i){
        row_to_try = i;
        if(pmdata[i*dim+i] == 0){
            do{
                ++row_to_try;
                if(row_to_try >= dim){
                    //printf("==inverse== No full rank matrix!(row_to_try = %d)\n", row_to_try);
                    //print_matrix(pmat);
                    memcpy(pmat->data, porig, data_size);
                    free(porig);
                    mat_free(&minv);
                    return 0;
                }
                val = pmat->data[row_to_try*dim+i];
            }while(val == 0);
            add_row(pmat, i, row_to_try);
            add_row(&minv, i, row_to_try);
        }

        //printf("[%d, %d] = %d\n",i,i,pmdata[i*dim+i]);
        //print_matrix(pmat);
        //print_matrix(&minv);

        if(pmdata[i*dim+i] != 1){
            val = gf->div(1, pmdata[i*dim+i]);
            irow(pmat, i, val, gf);
            irow(&minv, i, val, gf);
        }

        for(j = 0; j < dim; ++j){
            if(i == j){
                continue;
            }
            val = pmdata[j*dim+i];
            if(val == 0){
                continue;
            }
            add_irow(pmat, j, i, val, gf);
            add_irow(&minv, j, i, val, gf);
        }
    }

    memcpy(pmat->data, minv.data, data_size);

    free(porig);
    mat_free(&minv);
    return pmat->row;
}

int copy_matrix(gfmat_t * pmat_to, gfmat_t * pmat_from){
    int row, col;

    assert(pmat_from->row > 0);
    assert(pmat_from->col > 0);
    
    row = pmat_from->row;
    col = pmat_from->col;

    resize_matrix(pmat_to, row, col);
    memcpy(pmat_to->data, pmat_from->data, sizeofmat(row, col));

    return pmat_from->row;
}

int append_matrix(gfmat_t * pmat, gfmat_t * pmat_app){
    int row_ori;
    int col;
    size_t app_size;
    size_t offset;

    assert(pmat->data != NULL);
    assert(pmat->col == pmat_app->col);

    row_ori = pmat->row;
    col = pmat->col;

    pmat->row = pmat->row + pmat_app->row;
    pmat->data = (gfele_t *)realloc(pmat->data, ((size_t)(pmat->row))*((size_t)col)*sizeof(gfele_t));
    
    app_size = ((size_t)(pmat_app->row))*((size_t)col)*sizeof(gfele_t);
    offset = ((size_t)row_ori)*((size_t)col);
    memcpy(&(pmat->data[offset]), pmat_app->data, app_size);

    return pmat->row;
}

int append_part_of_matrix(gfmat_t * pmat, gfmat_t * pmat_app, int begin, int len){
    int row_ori;

    assert(pmat->data != NULL);
    assert(pmat->col == pmat_app->col);
    assert(begin >= 0);
    assert(begin+len <= pmat_app->row);

    row_ori = pmat->row;
    pmat->row += len;
    pmat->data = (gfele_t *)realloc(pmat->data, (pmat->row)*(pmat->col)*sizeof(gfele_t));

    memcpy(&(pmat->data[row_ori*(pmat->col)]), pmat_app->data, len*(pmat_app->col)*sizeof(gfele_t));

    return pmat->row;
}


int insert_matrix(gfmat_t * pmat, gfmat_t * pmat_inr, int pos_row){
    int row_ori;
    int col;
    int row_to_move;

    assert(pmat->data != NULL);
    assert(pos_row >= 0);
    assert(pos_row < pmat->row);
    assert(pmat->col == pmat_inr->col);

    col = pmat->col;
    row_ori = pmat->row;
    pmat->row += pmat_inr->row;

    pmat->data = (gfele_t *)realloc(pmat->data, (pmat->row)*(pmat->col)*sizeof(gfele_t));

    row_to_move = row_ori - pos_row;
    memmove(&(pmat->data[(pos_row+pmat_inr->row)*col]), &(pmat->data[pos_row*col]), row_to_move*col*sizeof(gfele_t));
    memcpy(&(pmat->data[pos_row*col]), pmat_inr->data, (pmat_inr->row)*col*sizeof(gfele_t));

    return pmat->row;
}

int insert_part_of_matrix(gfmat_t * pmat, gfmat_t * pmat_inr, int begin, int len){
    int row_ori;
    int col;
    int row_to_move;

    assert(pmat->data != NULL);
    assert(begin >= 0);
    assert(begin+len < pmat->row);
    assert(pmat->col == pmat_inr->col);

    col = pmat->col;
    row_ori = pmat->row;
    pmat->row += len;

    pmat->data = (gfele_t *)realloc(pmat->data, (pmat->row)*(pmat->col)*sizeof(gfele_t));

    row_to_move = row_ori - begin;
    memmove(&(pmat->data[(begin+len)*col]), &(pmat->data[begin*col]), row_to_move*col*sizeof(gfele_t));
    memcpy(&(pmat->data[begin*col]), pmat_inr->data, len*col*sizeof(gfele_t));

    return pmat->row;
}


int get_part_of_matrix(gfmat_t * pmat, gfmat_t * pmat_from, int begin, int len){
    int col;

    assert(pmat_from->data != NULL);
    assert(begin >= 0);
    assert(begin+len <= pmat_from->row);

    col = pmat_from->col;
    resize_matrix(pmat, len, col);

    memcpy(pmat->data, &(pmat_from->data[begin*col]), len*col*sizeof(gfele_t));

    return pmat->row;
}

int select_by_rows(gfmat_t * pmat_new, int *list, int num, gfmat_t *pmat_from){
    int i;
    int j;
    int row, col;
    gfele_t *pmdata;
    gfele_t *psrc;
    size_t totalsize;

    assert(pmat_from->data != NULL);
    assert(list != NULL);
    assert(num > 0);

    row = num;
    col = pmat_from->col;
    resize_matrix(pmat_new, row, col);

    pmdata = pmat_new->data;

    for(i = 0; i < num; ++i){
        if(list[i] >= pmat_from->row){
            printf("Error : selective row is out of range\n");
            return 0;
        }
        psrc = pmat_from->data;
        for(j = 0; j  < list[i]; ++j){
            psrc = psrc+col;
        }
        totalsize = ((size_t)col)*sizeof(gfele_t);
        memcpy(pmdata, psrc, totalsize);
        pmdata = pmdata+col;
    }

    return pmat_new->row;
}

int replace_matrix(gfmat_t * pmat, gfmat_t * pmat_rep, int begin, int len){
    int col;

    assert(pmat->data != NULL);
    assert(pmat_rep->data != NULL);
    assert(begin >= 0);
    assert(len <= pmat_rep->col);
    assert(begin+len <= pmat->row);
    assert(pmat->col == pmat_rep->col);

    col = pmat->col;

    memcpy(&(pmat->data[begin*col]), pmat_rep->data, len*col*sizeof(gfele_t));

    return pmat->row;
}


int wipe_matrix(gfmat_t * pmat, int begin, int len, gfele_t value){
    int i, j;

    assert(pmat->data != NULL);
    assert(begin >= 0);
    assert(begin+len <= pmat->row);

    for(i = begin; i < begin+len; ++i){
        for(j = 0; j < pmat->col; ++j){
            pmat->data[i*(pmat->col)+j] = value;
        }
    }

    return pmat->row;
}


int prod(gfmat_t * pmat_res, gfmat_t * pmat1, gfmat_t * pmat2, gfm_t * gf){
    int i, j;
    int row, col;
    gfele_t *psrc, *pdes;
    gfele_t val;

    assert(pmat1->data != NULL);
    assert(pmat2->data != NULL);
    assert(pmat1->col == pmat2->row);

    row = pmat1->row;
    col = pmat2->col;

    resize_matrix(pmat_res, row, col);
    memset(pmat_res->data, 0, sizeofmat(row, col));

    for(i = 0; i < pmat1->row; ++i){
        pdes = &(pmat_res->data[i*col]);
        for(j = 0; j < pmat1->col; ++j){
            val = pmat1->data[i*(pmat1->col)+j];
            psrc = &(pmat2->data[j*(pmat2->col)]);
            //for(k = 0; k < col; ++k){
            //    pdes[k] ^= gf->mul(psrc[k], val);
            //}
            gf->region_mul(pdes, psrc, val, col*sizeof(gfele_t), 1);
        }
    }

    return pmat_res->row;
}

typedef struct{
    gfmat_t *pa, *pb, *pc;
    int pnum;
    int thread_num;
    gfm_t *gf;
} thread_args_t;

static
void *run_prod_p(void *args){
    int i, j;
    thread_args_t *ta = (thread_args_t *)args;
    gfele_t *pad = ta->pa->data;
    gfele_t *pbd = ta->pb->data;
    gfele_t *pcd = ta->pc->data;
    int pnum = ta->pnum;
    gfm_t *gf = ta->gf;
    int row = ta->pa->row;
    int acol = ta->pa->col;
    int col = ta->pb->col;
    int m = ta->thread_num;

    for(i = pnum; i < row; i=i+m){
        for(j = 0; j < acol; ++j){
            //for(k = 0; k < col; ++k){
            //    pcd[i*col+k] ^= gf->mul(pad[i*acol+j], pbd[j*col+k]);
            //}
            gf->region_mul(&(pcd[i*col]), &(pbd[j*col]), pad[i*acol+j], col*sizeof(gfele_t), 1);
        }
    }

    return NULL;
}

int prod_p(gfmat_t * pmat_res, gfmat_t * pmat1, gfmat_t * pmat2, gfm_t *gf, int thread_num){
    int i;
    int row, col;
    int emes;
    pthread_t *tid;
    thread_args_t *tas;
    
    assert(pmat1->data != NULL);
    assert(pmat2->data != NULL);
    assert(pmat1->col == pmat2->row);

    row = pmat1->row;
    col = pmat2->col;

    resize_matrix(pmat_res, row, col);
    memset(pmat_res->data, 0, sizeofmat(row, col));

    if((pmat1->row) < thread_num){
        thread_num = pmat1->row;
    }

    tas = (thread_args_t *)malloc(thread_num*sizeof(thread_args_t));
    for(i = 0; i < thread_num; ++i){
        tas[i] = (thread_args_t){pmat1, pmat2, pmat_res, i, thread_num, gf};
    }

    tid = (pthread_t *)malloc(thread_num*sizeof(pthread_t));
    for(i = 0; i < thread_num; ++i){
        emes = pthread_create(&tid[i], NULL, run_prod_p, (void *)(&tas[i]));
        if(emes){
            printf("Error : pthread_create %d at thread%d", emes, i);
            exit(-1);
        }
    }

    for(i = 0; i < thread_num; ++i){
        emes = pthread_join(tid[i], NULL);
        if(emes){
            printf("Error : pthread_join %d at thread%d", emes, i);
            exit(-1);
        }
    }

    free(tid);
    free(tas);
    return pmat_res->row;
}


int transform_to_systematic(gfmat_t * pmat, gfm_t *gf){
    int i, j;
    int row, col;
    int iftrans = 0;
    int nz_row;
    gfele_t *pmdata;
    gfele_t divisor;
    
    if(pmat->row > pmat->col){
        transpose_matrix(pmat);
        iftrans = 1;
    }
    
    row = pmat->row;
    col = pmat->col;
    pmdata = pmat->data;
    
    for(i = 0; i < row; ++i){
        if(pmdata[i*col+i] == 0){
            nz_row = i+1;
            while(1){
                if(nz_row >= row){
                    printf("Error : No full rank matrix!\n");
                    print_matrix(pmat);
                    return 0;
                }
                if(pmdata[nz_row*col+i] != 0){
                    //add_row(i, nz_row);
                    region_xor_8(pmdata+i*col, pmdata+nz_row*col, col*sizeof(gfele_t));
                    break;
                }
                ++nz_row;
            }
        }
        divisor = gf->div(1, pmdata[i*col+i]);
        //gf->region_mul(&(pmdata[i*col]), &(pmdata[i*col]), divisor, col*sizeof(gfele_t), 0);
        irow(pmat, i, divisor, gf);
        for(j = 0; j < row; ++j){
            if(j == i){continue;}
            if(pmdata[j*col+i] == 0){continue;}
            add_irow(pmat, j, i, pmdata[j*col+i], gf);
        }
    }

    if(iftrans == 1){
        transpose_matrix(pmat);
    }

    return pmat->row;
}

int transform_to_bitmatrix(gfmat_t *pbmat, gfmat_t *pmat, gfm_t *gf, int word){
    gfele_t *pbuff;
    gfele_t val;
    int row = pmat->row;
    int col = pmat->col;
    int ww = word;
    int i, j, p, q;

    assert(pmat->data != NULL);

    pbuff = (gfele_t *)malloc(sizeofmat(row, col));
    memcpy(pbuff, pmat->data, sizeofmat(row, col));

    resize_matrix(pbmat, ww*row, ww*col);

    for(i = 0; i < row; ++i){
        for(j = 0; j < col; ++j){
            val = pbuff[i*col+j];
            for(p = 0; p < ww; ++p){
                for(q = 0; q < ww; ++q){
                    pbmat->data[(i*ww+q)*(ww*col)+j*ww+p] = ((val&(1<<q))?1:0);
                }
                val = gf->mul(val, 2);
            }
        }
    }

    free(pbuff);
    return row;
}
/* TODO : add resize_matrix for pdmat */
int select_nodes_of_vectors(gfmat_t *pdmat, gfmat_t *psmat, int *snl, int k){
    int alpha;
    int i;
    int col = pdmat->col;
    gfele_t * pmdata;

    alpha = (pdmat->row)/k;
    pmdata = pdmat->data;

    for(i = 0; i < k; ++i){
        memcpy(pmdata, psmat->data+col*snl[i]*alpha, alpha*col*sizeof(gfele_t));
        pmdata = pmdata+alpha*col;
    }

    return 1;
}
