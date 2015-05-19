#include "property.h"
#include "region_xor.h"
#include "algorithm.h"

int rank(gfmat_t * pmat, gfm_t *gf){
    int i, j, k;
    int row = pmat->row;
    int col = pmat->col;
    gfele_t *pmdata;
    gfele_t val;

    assert(pmat->data != NULL);
    assert(row >= 0);
    assert(col >= 0);

    pmdata = (gfele_t *)malloc(row*col*sizeof(gfele_t));

    memcpy(pmdata, pmat->data, row*col*sizeof(gfele_t));

    //loop all rows, jump out when reach end of row  or end of column
    for(i = 0, j = 0; (i < row)&&(j < col); ++i, ++j){  //i:row, j:col
        if(pmdata[i*col+j] == 0){//leading entry = 0
            for(k = i+1; k < row; ++k){
                if(pmdata[k*col+j] != 0){
                    region_xor_8(&(pmdata[i*col]), &(pmdata[k*col]), col*sizeof(gfele_t));
                    break;
                }    
            }    
            if(k >= row){//rest entries of this column equals 0  
                --i;                                        
                continue;
            }
        }
        val = gf->div(1, pmdata[i*col+j]);
        
        gf->region_mul(&(pmdata[i*col]), &(pmdata[i*col]), val, col*sizeof(gfele_t), 0);
        for(k = i+1; k < row; ++k){
            if(pmdata[k*col+j] == 0) continue;
            gf->region_mul(&(pmdata[k*col]), &(pmdata[i*col]), pmdata[k*col+j], col*sizeof(gfele_t), 1);
        }    
    }

    free(pmdata);
    return i;
}

int xrank(gfmat_t * pmat){
    int i, j, k;
    int row = pmat->row;
    int col = pmat->col;
    gfele_t *pmdata;

    assert(pmat->data != NULL);
    assert(row >= 0);
    assert(col >= 0);

    pmdata = (gfele_t *)malloc(row*col*sizeof(gfele_t));
    memcpy(pmdata, pmat->data, row*col*sizeof(gfele_t));

    //loop all rows, jump out when reach end of row  or end of column
    for(i = 0, j = 0; (i < row)&&(j < col); ++i, ++j){  //i:row, j:col
        if(pmdata[i*col+j] == 0){//leading entry = 0
            for(k = i+1; k < row; ++k){
                if(pmdata[k*col+j] != 0){
                    region_xor_8(&(pmdata[i*col]), &(pmdata[k*col]), col*sizeof(gfele_t));
                    break;
                }    
            }    
            if(k >= row){//rest entries of this column equals 0  
                --i;                                        
                continue;
            }
        }
        
        for(k = i+1; k < row; ++k){
            if(pmdata[k*col+j] == 0) continue;
            region_xor_8(&(pmdata[k*col]), &(pmdata[i*col]), col*sizeof(gfele_t));
        }    
    }

    free(pmdata);
    return i;
}

int invertible(gfmat_t * pmat, gfm_t *gf){
    int i, j, k;
    int row = pmat->row;
    int col = pmat->col;
    gfele_t *pmdata;
    gfele_t val;

    assert(pmat->data != NULL);
    assert(row >= 0);
    assert(col >= 0);

    pmdata = (gfele_t *)malloc(row*col*sizeof(gfele_t));

    memcpy(pmdata, pmat->data, row*col*sizeof(gfele_t));

    //loop all rows, jump out when reach end of row  or end of column
    for(i = 0, j = 0; (i < row)&&(j < col); ++i, ++j){  //i:row, j:col
        if(pmdata[i*col+j] == 0){//leading entry = 0
            for(k = i+1; k < row; ++k){
                if(pmdata[k*col+j] != 0){
                    region_xor_8(&(pmdata[i*col]), &(pmdata[k*col]), col*sizeof(gfele_t));
                    break;
                }    
            }    
            if(k >= row){//rest entries of this column equals 0  
                free(pmdata);
                return 0;                                        
            }
        }
        val = gf->div(1, pmdata[i*col+j]);
        
        gf->region_mul(&(pmdata[i*col]), &(pmdata[i*col]), val, col*sizeof(gfele_t), 0);
        for(k = i+1; k < row; ++k){
            if(pmdata[k*col+j] == 0) continue;
            gf->region_mul(&(pmdata[k*col]), &(pmdata[i*col]), pmdata[k*col+j], col*sizeof(gfele_t), 1);
        }    
    }

    free(pmdata);
    return row;
}

int mds_rs(gfmat_t *pmat, gfm_t *gf){
    int row, col;
    int *slist;
    int i;
    gfmat_t mat;
   
    assert(pmat->row > pmat->col);

    row = pmat->row;
    col = pmat->col;
    
    mat_init(&mat);

    slist = (int *)malloc(col*sizeof(int));
    for(i = 0; i < col; ++i){
        slist[i] = i;
    }

    do{
        select_by_rows(&mat, slist, col, pmat);
        if(invertible(&mat, gf) == 0){
            free(slist);
            mat_free(&mat);
            return 0;
        }
    }while(next_combination(slist, col, row) != 0);

    free(slist);
    mat_free(&mat);
    return 1;
}

int mds_msr(gfmat_t *pmat, int n, gfm_t *gf){
    int i;
    int k;
    int alpha;
    int row, col;
    int *snl;       //selective nodes' list
    gfmat_t matr;

    assert(pmat->row%n == 0);
    assert((pmat->col)%(pmat->row/n) == 0);
    assert(pmat->data != NULL);

    row = pmat->row;
    col = pmat->col;
    alpha = row/n;
    k = col/alpha;

    snl = (int *)malloc(k*sizeof(int));
    for(i = 0; i < k; ++i){
        snl[i] = i;
    }
    matr.row = col;
    matr.col = col;
    matr.data = (gfele_t *)malloc(col*col*sizeof(gfele_t));

    do{
        select_nodes_of_vectors(&matr, pmat, snl, k);
        if(!(invertible(&matr, gf))){
            free(matr.data);
            free(snl);
            return 0;
        }
    }while(next_combination(snl, k, n));

    free(matr.data);
    free(snl);
    return 1;
}

int xmds_msr(gfmat_t *pmat, int n){
    int i;
    int k;
    int alpha;
    int row, col;
    int *snl;       //selective nodes' list
    gfmat_t matr;

    assert(pmat->row%n == 0);
    assert((pmat->col)%(pmat->row/n) == 0);
    assert(pmat->data != NULL);

    row = pmat->row;
    col = pmat->col;
    alpha = row/n;
    k = col/alpha;

    snl = (int *)malloc(k*sizeof(int));
    for(i = 0; i < k; ++i){
        snl[i] = i;
    }
    matr.row = col;
    matr.col = col;
    matr.data = (gfele_t *)malloc(col*col*sizeof(gfele_t));

    do{
        select_nodes_of_vectors(&matr, pmat, snl, k);
        if(xrank(&matr) != col){
            /*printf("this matrix fail!\n");*/
            /*print_matrix(&matr);*/
            free(matr.data);
            free(snl);
            return 0;
        }
    }while(next_combination(snl, k, n));

    free(matr.data);
    free(snl);
    return 1;
}

int mds_msr_with_fnode(gfmat_t *pmat, int n, int fnode, gfm_t *gf){
    int i;
    int k;
    int alpha;
    int row, col;
    int *snl;
    gfmat_t matr;
    gfmat_t matp;

    row = pmat->row;
    col = pmat->col;
    alpha = row/n;
    k = col/alpha;

    mat_init(&matr);
    mat_init(&matp);
    matp.row = row;
    matp.col = col;
    matp.data = (gfele_t *)malloc(sizeofmat(row, col));
    if(fnode != n-1){
        if(fnode > 0){
            memcpy(matp.data, pmat->data, sizeofmat(fnode*alpha, col));
        }
        memcpy(matp.data+fnode*alpha*col, pmat->data+(fnode+1)*alpha*col, sizeofmat((n-fnode-1)*alpha, col));
        memcpy(matp.data+(n-1)*alpha*col, pmat->data+fnode*alpha*col, sizeofmat(alpha, col));
    }else{
        memcpy(matp.data, pmat->data, sizeofmat(row, col));
    }
    
    snl = (int *)malloc(k*sizeof(int));
    for(i = 0; i < k-1; ++i){
        snl[i] = i;
    }
    snl[k-1] = n-1;
    
    matr.row = col;
    matr.col = col;
    matr.data = (gfele_t *)malloc(col*col*sizeof(gfele_t));

    do{
        select_nodes_of_vectors(&matr, &matp, snl, k);
        if(!(invertible(&matr, gf))){
            mat_free(&matr);
            mat_free(&matp);
            free(snl);
            return 0;
        }
    }while(next_combination(snl, k-1, n-1));

    mat_free(&matr);
    mat_free(&matp);
    free(snl);
    return 1;
}

int mds_rc(gfmat_t *pmat, int n, int k, gfm_t *gf){
    int i;
    int alpha;
    int row, col;
    int *snl;       //selective nodes' list
    gfmat_t matr;

    assert(pmat->row%n == 0);
    assert(pmat->data != NULL);

    row = pmat->row;
    col = pmat->col;
    alpha = row/n;

    snl = (int *)malloc(k*sizeof(int));
    for(i = 0; i < k; ++i){
        snl[i] = i;
    }

    matr.row = k*alpha;
    matr.col = col;
    matr.data = (gfele_t *)malloc(k*alpha*col*sizeof(gfele_t));

    do{
        select_nodes_of_vectors(&matr, pmat, snl, k);
        if(rank(&matr, gf) < col){
            free(matr.data);
            free(snl);
            return 0;
        }
    }while(next_combination(snl, k, n));

    free(matr.data);
    free(snl);
    return 1;
}

int mds_rc_with_fnode(gfmat_t *pmat, int n, int k, int fnode, gfm_t *gf){
    int i;
    int alpha;
    int row, col;
    int *snl;
    gfmat_t matr;
    gfmat_t matp;

    row = pmat->row;
    col = pmat->col;
    alpha = row/n;

    mat_init(&matr);
    mat_init(&matp);

    matp.row = row;
    matp.col = col;
    matp.data = (gfele_t *)malloc(sizeofmat(row, col));
    
    if(fnode != n-1){
        if(fnode > 0){
            memcpy(matp.data, pmat->data, sizeofmat(fnode*alpha, col));
        }
        memcpy(matp.data+fnode*alpha*col, pmat->data+(fnode+1)*alpha*col, sizeofmat((n-fnode-1)*alpha, col));
        memcpy(matp.data+(n-1)*alpha*col, pmat->data+fnode*alpha*col, sizeofmat(alpha, col));
    }else{
        memcpy(matp.data, pmat->data, sizeofmat(row, col));
    }
    
    snl = (int *)malloc(k*sizeof(int));
    for(i = 0; i < k-1; ++i){
        snl[i] = i;
    }
    snl[k-1] = n-1;
    
    matr.row = k*alpha;
    matr.col = col;
    matr.data = (gfele_t *)malloc(k*alpha*col*sizeof(gfele_t));

    do{
        select_nodes_of_vectors(&matr, &matp, snl, k);
        if(rank(&matr, gf) < col){
            mat_free(&matr);
            mat_free(&matp);
            free(snl);
            return 0;
        }
    }while(next_combination(snl, k-1, n-1));

    mat_free(&matr);
    mat_free(&matp);
    free(snl);
    return 1;
}

static 
int select_nodes_of_vectors_coomat(coomat_t *pcmat1, coomat_t *pcmat2, int *snl, int k){
    int alpha;
    int i;
    int row = pcmat1->lil_pos.row;
    int col = pcmat1->lil_pos.col;
    gfele_t *pldata, *pmdata;
    
    alpha = row/k;
    pldata = pcmat1->lil_pos.data;
    pmdata = pcmat1->mat_val.data;
    
    for(i = 0; i < k; ++i){
        memcpy(pldata, pcmat2->lil_pos.data+col*snl[i]*alpha, alpha*col*sizeof(gfele_t));
        memcpy(pmdata, pcmat2->mat_val.data+col*snl[i]*alpha, alpha*col*sizeof(gfele_t));

        pmdata = pmdata + alpha*col;
        pldata = pldata + alpha*col;
    }
    
    return 0;
}

int mds_coomat(coomat_t *pcmat, int n, gfm_t *gf){
    int i;
    int k;
    int alpha;
    int row, col, rawcol;
    int *snl;       //selective nodes' list
    coomat_t matr;

    row = pcmat->lil_pos.row;
    col = pcmat->lil_pos.col;
    rawcol = pcmat->lil_pos.rawcol;
    alpha = row/n;
    k = rawcol/alpha;

    snl = (int *)malloc(k*sizeof(int));
    for(i = 0; i < k; ++i){
        snl[i] = i;
    }
    matr.lil_pos.data = (gfele_t *)malloc(rawcol*col*sizeof(gfele_t));
    matr.mat_val.data = (gfele_t *)malloc(rawcol*col*sizeof(gfele_t));

    do{
	    matr.lil_pos.row = rawcol;
	    matr.lil_pos.col = col;
	    matr.lil_pos.rawcol = rawcol;
	    matr.mat_val.row = rawcol;
	    matr.mat_val.col = col;
        
        select_nodes_of_vectors_coomat(&matr, pcmat, snl, k);
        /*printf("candidate matrix\n");*/
        /*print_coomat(&matr);*/
        /*getchar();*/
        if(inverse_coomat(&matr, gf) != 0){
            /*printf("ungratified nodes:");*/
            /*for(i = 0; i < k; ++i){*/
                /*printf("%d ",snl[i]);*/
            /*}*/
            /*printf("\n");*/
            free(matr.lil_pos.data);
            free(matr.mat_val.data);
            free(snl);
            return 0;
        }
    }while(next_combination(snl, k, n));

    free(matr.lil_pos.data);
    free(matr.mat_val.data);
    free(snl);
    return 1;
}

/*
 * TODO
static
int exist_dvecs(gfmat_t * pmat, int d){
    int *snl;
    int alpha, k;

    alpha = pmat->row/d;
    k = pmat->col/alpha;

    snl = (int *)malloc(k*sizeof(gfele_t));

    free(snl);
}

int rmds_msr(gfmat_t *pmat, int n, gfm_t *gf){
    int alpha;
    int i;
    gfmat_t mat;
    
    mat_init(&mat);
    alpha = pmat->row/n;

    for(i = 0; i < n; i++){
        copy_matrix(&mat, pmat);
        del_rows(&mat, i*alpha, alpha);
        if(!exist_dvecs(&mat, n-1)){
            mat_free(&mat);
            return false;
        }
    }

    mat_free(&mat);
    return pmat->row;
}
*/
