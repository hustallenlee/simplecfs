/*
 *  zcode_struct.c
 *  
 *
 */

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "zcode_struct.h"

/*
 ************  ZMAT *************
 */


int mat_k2m2[16] = {\
    1, 0, 1, 0, 
    0, 1, 0, 1, 
    1, 0, 0, 1, 
    0, 1, 1, 0\
};

int mat_k2m3[54] = {\
    1, 0, 0, 1, 0, 0, 
    0, 1, 0, 0, 1, 0, 
    0, 0, 1, 0, 0, 1, 
    1, 0, 0, 0, 0, 1, 
    0, 1, 0, 1, 0, 0, 
    0, 0, 1, 0, 1, 0, 
    1, 0, 0, 0, 1, 0, 
    0, 1, 0, 0, 0, 1, 
    0, 0, 1, 1, 0, 0\
};

int mat_k2m4[128] = {\
    1, 0, 0, 0, 1, 0, 0, 0, 
    0, 1, 0, 0, 0, 1, 0, 0, 
    0, 0, 1, 0, 0, 0, 1, 0, 
    0, 0, 0, 1, 0, 0, 0, 1, 
    1, 0, 0, 0, 0, 0, 0, 1, 
    0, 1, 0, 0, 1, 0, 0, 0, 
    0, 0, 1, 0, 0, 1, 0, 0, 
    0, 0, 0, 1, 0, 0, 1, 0, 
    1, 0, 0, 0, 0, 0, 1, 0, 
    0, 1, 0, 0, 0, 0, 0, 1, 
    0, 0, 1, 0, 1, 0, 0, 0, 
    0, 0, 0, 1, 0, 1, 0, 0, 
    1, 0, 0, 0, 0, 1, 0, 0, 
    0, 1, 0, 0, 0, 0, 1, 0, 
    0, 0, 1, 0, 0, 0, 0, 1, 
    0, 0, 0, 1, 1, 0, 0, 0\
};

static
int init_zmat(zmat_t *pzmat, int m, int k){
    pzmat->row = ZMAT_ROW(m, k);
    pzmat->col = ZMAT_COL(m, k);
    if((pzmat->data = ZMAT_DATA_ALLOC(m, k)) == NULL){
        printf("ERROR : fail to alloc mem for the mati data!\n");
        return 0;
    }

    return 1;
}

static
int mat_k2(zmat_t *pm, int m){
    switch(m){
        case 2:
            memcpy(pm->data, &mat_k2m2[0], 16*sizeof(int));
            break;
        case 3:
            memcpy(pm->data, &mat_k2m3[0], 54*sizeof(int));
            break;
        case 4:
            memcpy(pm->data, &mat_k2m4[0], 128*sizeof(int));
            break;
        default:
            printf("m only equals to 2,3,4\n");
            return 0;
    }

    return 1;
}

static
int mat_ins_k(zmat_t *pm_new, zmat_t *pm_ori, int m, int k){
    int row_ori, col_ori;
    int col_new;
    int i, j, p;
    int inc;
    int pos;

    row_ori = ZMAT_ROW(m, k);
    col_ori = ZMAT_COL(m, k);
    col_new = ZMAT_COL(m, k+1);
    
    for(i = 0; i < row_ori; ++i){
        for(j = 0; j < col_ori; ++j){
            if(pm_ori->data[i*col_ori+j] == 0) continue;
            pos = (i*m)*col_new+(j*m);
            for(p = 0; p < m; ++p){
                inc = p*col_new+p;
                pm_new->data[pos+inc] = 1;
            }
        }
    }
    
    //last column
    for(i = 0; i < row_ori; ++i){
        int shift = i/ZMAT_R(m,k);
        for(j = (k-1)*ZMAT_R(m,k); j < col_ori; ++j){
            if(pm_ori->data[i*col_ori+j] == 0) continue;
            pos = (i*m)*col_new+(j*m+ZMAT_R(m,k+1));
            for(p = 0; p < m; ++p){
                if(shift+p < m){
                    inc = p*col_new+p+shift*col_new;
                }else{
                    inc = p*col_new+p+(shift-m)*col_new;
                }
                pm_new->data[pos+inc] = 1;
            }
        }
    }
    return 1;
}

int make_z_mat(zmat_t *pzmat, int m, int k){
    int ki;
    zmat_t mat1, mat2;

    mat_init(&mat1);
    mat_init(&mat2);

    if((m > 4)|(m < 2)){
        printf("Error: m must be one of 2/3/4\n");
        return 0;
    }    

    init_zmat(pzmat, m, k);
    ki = 2;
    init_zmat(&mat1, m, ki);
    mat_k2(&mat1, m);

    if(k > 2){
        for(ki = 3; ki <= k; ++ki){
            mat_free(&mat2);
            init_zmat(&mat2, m, ki);
            mat_ins_k(&mat2, &mat1, m, ki-1);
            mat_free(&mat1);
            init_zmat(&mat1, m, ki);
            memcpy(mat1.data, mat2.data, ZMAT_ROW(m, ki)*ZMAT_COL(m, ki)*sizeof(gfele_t));
        }
        memcpy(pzmat->data, mat2.data, ZMAT_ROW(m, k)*ZMAT_COL(m, k)*sizeof(gfele_t));
    }else{
        memcpy(pzmat->data, mat1.data, ZMAT_ROW(m, k)*ZMAT_COL(m, k)*sizeof(gfele_t));
    }

    mat_free(&mat1);
    mat_free(&mat2);

    return 1;
}

int make_zg_mat(zmat_t *pzmat, gfmat_t *pmat, int m, int k){
    int i, j;
    int r;
    int row, col;
    gfele_t val;

    make_z_mat(pzmat, m, k);

    row = pzmat->row;
    col = pzmat->col;
    r = ZMAT_R(m, k);

    for(i = 0; i < row; ++i){
        for(j = 0; j < col; ++j){
            if(pzmat->data[i*col+j] != 0){
                val = get(pmat, i/r, j/r);
                pzmat->data[i*col+j] = val;
            }
        }
    }

    return row;
}

void print_zmat_bit(zmat_t * pzmat, int m){
    int i, j;
    int temp;
    int r = (pzmat->row)/m;

    temp = r-2;
    for(i = 0; i < pzmat->row; ++i){
        for(j = 0; j < pzmat->col; ++j){
            ++temp;
            if(temp%r==r-1){
                printf(" ");
            }
            if(pzmat->data[i*(pzmat->col)+j] == 1){
                printf("1");
            }else{
                printf(" ");
            }
        }
        if(i%r == r-1){
            printf("\n");
        }
        printf("\n");
    }

}

/*
 ************  ZLIL *************
 */
static int lil_k2m2[8] = {
    0,2,
    1,3,
    0,3,
    1,2
};

static int lil_k2m3[18] = {
    0,3,
    1,4,
    2,5,
    0,5,
    1,3,
    2,4,
    0,4,
    1,5,
    2,3
};

static int lil_k2m4[32] = {
    0,4,
    1,5,
    2,6,
    3,7,
    0,7,
    1,4,
    2,5,
    3,6,
    0,6,
    1,7,
    2,4,
    3,5,
    0,5,
    1,6,
    2,7,
    3,4
};

static
int init_zlil(lil_t *pzlil, int m, int k){
    pzlil->row = ZLIL_ROW(m, k);
    pzlil->col = ZLIL_COL(m, k);
    pzlil->rawcol = ZMAT_COL(m, k);
    if((pzlil->data = ZLIL_DATA_ALLOC(m, k)) == NULL){
        printf("ERROR : fail to alloc mem for the mati data!\n");
        return 0;
    }

    return 1;
}

static
int lil_k2(lil_t *lilk2, int m){
    switch(m){
        case 2:
            memcpy(lilk2->data, &lil_k2m2[0], 8*sizeof(int));
            break;
        case 3:
            memcpy(lilk2->data, &lil_k2m3[0], 18*sizeof(int));
            break;
        case 4:
            memcpy(lilk2->data, &lil_k2m4[0], 32*sizeof(int));
            break;
        default:
            printf("m only must be 2,3,4\n");
            return 0;
    }

    return 1;
}


static 
inline
int region_mul_plus(gfele_t *preg, int mul, int add, int len){
    int i;

    for(i = 0; i < len; ++i){
        *(preg+i) = (*(preg+i))*mul+add;
    }

    return len;
}

static
int lil_ins_k(lil_t *lil_new, lil_t *lil_ori, int m, int k){
    int r;
    int add;
    int i,j;
    gfele_t * psrc = lil_ori->data;
    gfele_t * pdes = lil_new->data;
    gfele_t tmp;

    r = ZLIL_R(m, k);

    /* nodes */ 
    for(i = 0; i < m; ++i){
        for(j = 0; j < r; ++j){
            for(add = 0; add < m; add++){
                memcpy(pdes, psrc, k*sizeof(gfele_t));
                region_mul_plus(pdes, m, add, k);
                pdes = pdes+k;
                /* last node */
                tmp = *(pdes-1)-(add)+r*m;
                /*printf("r=%d,add=%d***%d***\n",r,add,tmp);*/
                (*pdes) = (tmp/m)*m + (m-i+add)%m;
                pdes++;
            }
            psrc = psrc+k;
        }
    }

    return 1;
}


int make_z_lil(lil_t *pzlil, int m, int k){
    lil_t lt1, lt2;
    int ki;

    lt1.data = NULL;
    lt2.data = NULL;

    if((m > 4)||(m < 2)){
        printf("Error: m must be one of 2/3/4\n");
        return 0;
    }
    
    init_zlil(pzlil, m, k);
    ki = 2;
    init_zlil(&lt1, m, ki);
    lil_k2(&lt1, m);

    if(k > 2){
        for(ki = 3; ki <= k; ++ki){
            zlil_free(&lt2);
            init_zlil(&lt2, m, ki);
            lil_ins_k(&lt2, &lt1, m, ki-1);
            zlil_free(&lt1);
            init_zlil(&lt1, m, ki);
            memcpy(lt1.data, lt2.data, ZLIL_ROW(m,ki)*ZLIL_COL(m, ki)*sizeof(gfele_t));
        }
        memcpy(pzlil->data, lt2.data, ZLIL_ROW(m,k)*ZLIL_COL(m,k)*sizeof(gfele_t));
    }else{
        memcpy(pzlil->data, lt1.data, ZLIL_ROW(m,k)*ZLIL_COL(m,k)*sizeof(gfele_t));
    }

    zlil_free(&lt1);
    zlil_free(&lt2);

    return pzlil->row;
}

void zlil_free(lil_t *pzlil){
    if(pzlil->data != NULL){
        free(pzlil->data);
        pzlil->data = NULL;
    }
}

void print_lil(lil_t *pzlil){
    int i, j; 
    int row, col;

    row = pzlil->row;
    col = pzlil->col;

    for(i = 0; i < row; i++){
        for(j = 0; j < col; ++j){
            printf("%3d ", *(pzlil->data+i*col+j));
        }
        printf("\n");
    }
}

static
int get_data_list(int *dptr, int fnode, int m, int k, int cirlen, int brklen, int durlen){
    int i, p, q;
    int times;
    int *ptr_list;
    int r = ZMAT_R(m, k);
    int val;
    int count=0;

    times = ((r/cirlen)>0)?(r/cirlen):1;
    
    ptr_list = dptr;
    for(p = 0; p < k; ++p){ /* nodes*/
        if(p == fnode)  continue;
	    for(i = 0; i < times; ++i){ /* circles */
            val = p*r+i*cirlen;
	        while((val < p*r+(i+1)*cirlen)&&(val < r*(p+1))){    /* brkcircle*/
                for(q = 0; q < durlen; ++q){
                    *ptr_list = val;
                    ++ptr_list;
                    ++val;
                    ++count;
                }
                val = val+(brklen-durlen);
	        }
	    }
    }


    return count;
}

static
int get_parity_list(int *pptr, int m, int k, int cirlen, int brklen, int durlen){
    int i, p, q;
    int times;
    int *ptr_list;
    int r = ZMAT_R(m, k);
    int val;
    int count = 0;

    times = ((r/cirlen)>0)?(r/cirlen):1;

    ptr_list = pptr;
    for(p = 0; p < m; ++p){ /* nodes*/
	    for(i = 0; i < times; ++i){ /* circles */
            val = p*r+i*cirlen;
	        while((val < p*r+(i+1)*cirlen)&&(val < r*(p+1))){    /* brkcircle*/
                for(q = 0; q < durlen; ++q){
                    *ptr_list = val;
                    ++ptr_list;
                    ++val;
                    ++count;
                }
                val = val+(brklen-durlen);
	        }
	    }
    }

    return count;
}

static
int get_f0_parity_list(int *pptr, int m, int k){
    int i, j;
    int r;
    int *ptr_list;
    int length;
    int val;

    r = ZMAT_R(m, k);
    length = r/m;

    for(i = 0; i < m; ++i){
        ptr_list = pptr + i*length;
        for(j = 0; j < length; ++j){
            val = i*(r+length)+j;
            ptr_list[j] = val;
        }
    }

    return length;
}

int **get_repair_list(int m, int k, int fnode){
    int **dplist;
    int *dptr;
    int *pptr;
    int num_per_node;
    int r;
    int i;
    int cirlen, brklen, durlen;

    r = ZMAT_R(m, k);
    num_per_node = r/m;

    if((dplist = (int **)malloc(2*sizeof(int *))) == NULL){
        printf("ERROR : fail to malloc !\n");
        return 0;
    }
    if((dptr = (int *)malloc((k-1)*num_per_node*sizeof(int))) == NULL){
        printf("ERROR : fail to malloc !\n");
        return 0;
    }
    if((pptr = (int *)malloc(m*num_per_node*sizeof(int))) == NULL){
        printf("ERROR : fail to malloc !\n");
        return 0;
    }
    dplist[0] = dptr;
    dplist[1] = pptr;

    /* fnode = 0 */
    cirlen = r*m;
    brklen = r+r/m;
    durlen = r/m;
    i = fnode;
    
    /* if fnode > 0, do sth. */
    while(i >= 1){
        cirlen = cirlen/m;
        brklen = brklen/m;
        durlen = durlen/m;
        --i;
    }
    if(fnode == k-1){
        cirlen = m;
        brklen = m;
        durlen = 1;
    }

    //printf("inter : %d, length %d\n",interval,length);
    get_data_list(dptr, fnode, m, k, cirlen, brklen, durlen);
    /*printf("  datalist len:%d\n",retval);*/
    if(fnode == 0){
        get_f0_parity_list(pptr, m, k);
    }else{
        get_parity_list(pptr, m, k, cirlen, brklen, durlen);
    }
    /*printf("paritylist len:%d\n",retval);*/

    return dplist;
}

void print_repair_list(int **dplist, int m, int k){
    int num_per_node;
    int r = ZMAT_R(m, k);
    int num_data;
    int num_parity;
    int i;

    num_per_node = r/m;
    num_data = (k-1)*num_per_node;
    num_parity = m*num_per_node;

    printf(" data list\t");
    for(i = 0; i < num_data; ++i){
        printf("%3d ",dplist[0][i]);
    }
    printf("\n");

    printf("parity list\t");
    for(i = 0; i < num_parity; ++i){
        printf("%3d ",dplist[1][i]);
    }
    printf("\n");

}

/*
 ************  COOMAT  *************
 */

int mtimes_copy_matrix(gfmat_t * pmat_to, gfmat_t * pmat_from, int mul){
    int row, col;
    gfele_t *ptr_data;
    int i, j;
    gfele_t val;

    assert(pmat_from->row > 0);
    assert(pmat_from->col > 0);
    
    row = mul*(pmat_from->row);
    col = pmat_from->col;

    if((pmat_to->data = (gfele_t *)malloc(sizeofmat((size_t)row, col))) == NULL){
        printf("ERROR: Fail to alloc mem for the mat_val matrix!\n");
        return 0;
    }

    ptr_data = pmat_to->data;
    for(i = 0; i < row; i++){
        for(j = 0; j < col; j++){
            val = get(pmat_from, i/mul, j);
            *ptr_data = val;
            ptr_data++;
        }
    }

    return pmat_from->row;
}

int make_z_coomat(coomat_t *pzcoomat, zmat_t *pmat, int m, int k){
    int r;
    int row, col;

    if(pmat->row == ZLIL_ROW(m, k)){
        pzcoomat->type = 17;
    }else{
        if(pmat->row == m){
            pzcoomat->type = 16;
        }else{
            printf("ERROR: Conflicting number of rows: lil_row: %d, mat_row: %d\n", m*ZLIL_R(m,k), pmat->row);
            return 0;
        }
    }

    if(pmat->col != k){
        printf("ERROR: Conflicting number of cols: lil_col : %d, mat_col: %d", k, pmat->col);
        return 0;
    }
    
    r = ZLIL_R(m, k);

    make_z_lil(&(pzcoomat->lil_pos), m, k);
    mat_init(&(pzcoomat->mat_val));
    if(pzcoomat->type == 17){
        copy_matrix(&(pzcoomat->mat_val), pmat);
    }else{
        mtimes_copy_matrix(&(pzcoomat->mat_val), pmat, r);
    }

    row = pzcoomat->lil_pos.row;
    col = pzcoomat->lil_pos.col;

    return row+col;
}

int  print_coomat(coomat_t * pzcoomat){
    int i, j;
    int row, col;

    row = pzcoomat->lil_pos.row;
    col = pzcoomat->lil_pos.col;
    
    for(i = 0; i < row; ++i){
        for(j = 0; j < col; ++j){
            printf("%3x ", pzcoomat->lil_pos.data[i*col+j]);
        }
        printf("  \t");
        for(j = 0; j < col; ++j){
            printf("%3x ", pzcoomat->mat_val.data[i*col+j]);
        }
        printf("\n");
    }


    return row;
}

void zcoomat_free(coomat_t *pzcoomat){
    zlil_free(&(pzcoomat->lil_pos));
    mat_free(&(pzcoomat->mat_val));
}

/*
 ************  OTHERS  *************
 */

void dump_gfmat(zmat_t *pm, int m, int k, char *filename){
    int i, j;
    FILE *fp;

    if(!(fp = fopen(filename, "w+"))){
        printf("cann't open the file : %s\n", filename);
    exit(0);
    }

    fprintf(fp, "m:%d\n", m);
    fprintf(fp, "k:%d\n", k);
    fprintf(fp, "row:%d\n", pm->row); 
    fprintf(fp, "col:%d\n", pm->col);
    for(i = 0; i < pm->row; ++i){
        for(j = 0; j < pm->col; ++j){
            fprintf(fp, "%d\t", pm->data[i*(pm->col)+j]);
        }
        fprintf(fp, "\n");
    } 

    fclose(fp);
}

void dump_lil(lil_t *pzlil, int m, int k, char *filename){
    int i, j;
    FILE *fp;

    if(!(fp = fopen(filename, "w+"))){
        printf("cann't open the file : %s\n", filename);
        exit(0);
    }

    fprintf(fp, "m:%d\n", m);
    fprintf(fp, "k:%d\n", k);
    fprintf(fp, "row:%d\n", pzlil->row);
    fprintf(fp, "col:%d\n", pzlil->col);
    fprintf(fp, "rawcol:%d\n", pzlil->rawcol);
    for(i = 0; i < pzlil->row; ++i){
        for(j = 0; j < pzlil->col; ++j){
            fprintf(fp, "%d\t", pzlil->data[i*(pzlil->col)+j]);
        }
        fprintf(fp, "\n");
    }

    fclose(fp);
}

static
int get_number_of_ones_in_a_row(zmat_t *pzmat){
    int count = 0;
    int col = pzmat->col;
    int i;

    for(i = 0; i < col; ++i){
        if(pzmat->data[i] != 0){
            count++;
        }
    }

    return count;
}

int zmat_to_lil(lil_t *pzlil, zmat_t *pzmat){
    int i, j;
    int lrow, lcol;
    int mrow, mcol;
    int index;

    lrow = pzmat->row;
    lcol = get_number_of_ones_in_a_row(pzmat);
    mrow = pzmat->row;
    mcol = pzmat->col;
    
    if((pzlil->data = (gfele_t *)calloc(1, sizeofmat((size_t)lrow, lcol))) == NULL){
        printf("ERROR: Fail to alloc mem for the matrix!\n");
        return 0;
    }
    
    index = 0;
    for(i = 0; i < mrow; ++i){
        for(j = 0; j < mcol; ++j){
            if(pzmat->data[i*mcol+j] != 0){
                pzlil->data[index] = j;
                index++;
            }
        }
    }
    pzlil->row = lrow;
    pzlil->col = lcol;
    pzlil->rawcol = mcol;

    return lcol;
}

int lil_to_zmat(zmat_t *pzmat, lil_t *pzlil){
    int mrow = pzlil->row;
    int col = pzlil->col;
    int mcol = pzlil->rawcol;
    int i, j;
    gfele_t val;

    if((pzmat->data = (gfele_t *)calloc(1, sizeofmat((size_t)mrow, mcol))) == NULL){
        printf("ERROR: Fail to alloc mem for the matrix!\n");
        return 0;
    }
    
    for(i =0; i < mrow; ++i){
        for(j = 0; j < col; ++j){
            val = pzlil->data[i*col+j];
            if (j!=0 && val==0) {
                break;
            }
            pzmat->data[i*mcol+val] = 1;
        }
    }
    pzmat->row = mrow;
    pzmat->col = mcol;

    return mrow;
}

// attention: 
//  each row of @pzmat should not be all zero
//  不对齐的部分用在@pzcoomat的位置和值中用0表示 
int zmat_to_coomat(coomat_t *pzcoomat, zmat_t *pzmat){
    pzcoomat->type = 17;

    int i, j, k;
    int rawcol = pzmat->col;
    int col, max=0;
    int row = pzmat->row;
    pgfmat_t pmat_val = &(pzcoomat->mat_val);
    lil_t *plil_pos = &(pzcoomat->lil_pos);

    // get max col for coomat
    for (i = 0; i < pzmat->row; i++) {
        col = 0;
        for (j = 0; j < pzmat->col; j++) {
            if (pzmat->data[i*rawcol+j]) {
                col ++;
            }
        }
        if (max < col) {
            max = col;
        }
    }
    col = max; 

    mat_init(pmat_val);
    make_zero(pmat_val, row, col);
    plil_pos->data = (gfele_t*)calloc(1, sizeof(gfele_t)*row*col);
    plil_pos->row = row;
    plil_pos->col = col;
    plil_pos->rawcol = rawcol;

    for (i = 0; i < row; i++) {
        k = 0;
        for (j = 0; j < rawcol; j++) {
            if (pzmat->data[i*rawcol+j]) {
                pmat_val->data[i*col+k] = pzmat->data[i*rawcol+j];
                plil_pos->data[i*col+k] = j;
                k++;
            }
        }
    }
    pzcoomat->type = 17;
    
    return pzcoomat->type;
}


int coomat_to_zmat(zmat_t *pzmat, coomat_t *pzcoomat){
    int i, j, k;
    int rawcol = pzcoomat->lil_pos.rawcol;
    int row = pzcoomat->lil_pos.row;
    int col = pzcoomat->lil_pos.col;

    make_zero(pzmat, row, rawcol);
    for (i = 0; i < row; i++) {
        for (j = 0; j < col; j++) {
            k = pzcoomat->lil_pos.data[i*col+j];
            if (j!=0 && k==0) {
                break;
            }
            pzmat->data[i*rawcol+k] = pzcoomat->mat_val.data[i*col+j];
        }
    }

    return pzcoomat->type; 
}

void extend_to_systematic_coomat(coomat_t *pcmat, int m, int k){
    int r;
    int i;
    gfele_t *pmdata, *pldata;

    r = ZLIL_R(m, k);
    pmdata = (gfele_t *)malloc((m+k)*r*k*sizeof(gfele_t));
    memset(pmdata, 0, (m+k)*r*k*sizeof(gfele_t));
    pldata = (gfele_t *)malloc((m+k)*r*k*sizeof(gfele_t));
    memset(pldata, 0, (m+k)*r*k*sizeof(gfele_t));

    for(i = 0; i < k*r; ++i){
        pldata[i*k] = i;
        pmdata[i*k] = 1;
    }    
    memcpy(pldata+k*r*k, pcmat->lil_pos.data, m*r*k*sizeof(gfele_t));
    memcpy(pmdata+k*r*k, pcmat->mat_val.data, m*r*k*sizeof(gfele_t));

    free(pcmat->lil_pos.data);
    free(pcmat->mat_val.data);

    pcmat->lil_pos.data = pldata;
    pcmat->mat_val.data = pmdata;
    pcmat->lil_pos.row = (m+k)*r;
    pcmat->mat_val.row = (m+k)*r;
}



