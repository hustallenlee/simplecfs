#include "mcoding.h"
#include "string.h"
#include "region_xor.h"

#define segment_size 256

int get_block_size(int file_size, gfmat_t *pmat){
    int col;
    int block_size;

    col = pmat->col;
               
    if( file_size%(segment_size*col) == 0 ){ 
        block_size = file_size/col;
    }else{
        block_size = (file_size/(col*segment_size)+1)*segment_size;
    }  

    return block_size;
}

int get_block_size_by_col(int file_size, int col){
    int block_size;

    if( file_size%(segment_size*col) == 0 ){ 
        block_size = file_size/col;
    }else{
        block_size = (file_size/(col*segment_size)+1)*segment_size;
    }  

    return block_size;
}

/*
 * RS coding
 */

int mcoding_dg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat, gfm_t *gf){
    int i, j;
    int row, col;
    int bgfsize;
    gfele_t *pgdes, *pgsrc;
    gfele_t val;

    row = pmat->row;
    col = pmat->col;
    bgfsize = block_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    pgsrc = (gfele_t *)psrc;
    for(j = 0; j < col; ++j){
        pgdes = (gfele_t *)pdes;
        for(i = 0; i < row; ++i){
            val = pmat->data[i*col+j];
            if(val != 0){
                gf->region_mul(pgdes, pgsrc, val, block_size, 1);
            }
            pgdes = pgdes + bgfsize;
        }
        pgsrc = pgsrc + bgfsize;
    }

    return 1;
}

int mcoding_pg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat, gfm_t *gf){
    int i, j;
    int row, col;
    int bgfsize;
    gfele_t *pgdes, *pgsrc;
    gfele_t val;

    row = pmat->row;
    col = pmat->col;
    bgfsize = block_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    pgdes = (gfele_t *)pdes;
    for(i = 0; i < row; ++i){
        pgsrc = (gfele_t *)psrc;
        for(j = 0; j < col; ++j){
            val = pmat->data[i*col+j];
            if(val != 0){
                gf->region_mul(pgdes, pgsrc, val, block_size, 1);
            }
            pgsrc = pgsrc + bgfsize;
        }
        pgdes = pgdes + bgfsize;
    }

    return 1;
}

int mcoding_pbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgdes = pgdes + pgfsize;
                    pgsrc = pgsrc + pgfsize;
                }
            }
        }
    }else{
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgdes = pgdes + pgfsize;
                    pgsrc = pgsrc + pgfsize;
                }
                gf->region_mul(pgdes, pgsrc, val, rest_size, 1);   
            }
        }
    }
    return 1;
}

int mcoding_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    rest_size = block_size - times*packet_size;
    if(rest_size == 0){
        pgdes = (gfele_t *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (gfele_t *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgsrc = pgsrc + bgfsize;
                }
                pgdes = pgdes + pgfsize;
            }
        }
    }else{
        pgdes = (gfele_t *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (gfele_t *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgsrc = pgsrc + bgfsize;
                }
                pgdes = pgdes + pgfsize;
            }
            pgsrc = (gfele_t *)(psrc + times*packet_size);
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val != 0){
                    gf->region_mul(pgdes, pgsrc, val, rest_size, 1);   
                }
                pgsrc = pgsrc + bgfsize;
            }
            pgdes = pgdes + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}

int mcoding_dpg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;
   
    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        pgsrc = (gfele_t *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (gfele_t *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgdes = pgdes + bgfsize;
                }
                pgsrc = pgsrc + pgfsize;
            }
        } 
    }else{
        pgsrc = (gfele_t *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (gfele_t *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgdes = pgdes + bgfsize;
                }
                pgsrc = pgsrc + pgfsize;
            }
            pgdes = (gfele_t *)(pdes+ times*packet_size);
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val != 0){
                    gf->region_mul(pgdes, pgsrc, val, rest_size, 1);   
                }
                pgdes = pgdes + bgfsize;
            }
            pgsrc = pgsrc + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}


int mcoding_dbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgsrc = pgsrc+pgfsize;
                    pgdes = pgdes+pgfsize;
                }
            }
        }
    }else{
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gf->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgsrc = pgsrc+pgfsize;
                    pgdes = pgdes+pgfsize;
                }
                    gf->region_mul(pgdes, pgsrc, val, rest_size, 1);
            }
        }
    }

    return 1;
}

int mcoding_pbg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgdes = pgdes + pgfsize;
                    pgsrc = pgsrc + pgfsize;
                }
            }
        }
    }else{
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgdes = pgdes + pgfsize;
                    pgsrc = pgsrc + pgfsize;
                }
                gfs->region_mul(pgdes, pgsrc, val, rest_size, 1);   
            }
        }
    }
    return 1;
}

int mcoding_ppg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    rest_size = block_size - times*packet_size;
    if(rest_size == 0){
        pgdes = (gfele_t *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (gfele_t *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgsrc = pgsrc + bgfsize;
                }
                pgdes = pgdes + pgfsize;
            }
        }
    }else{
        pgdes = (gfele_t *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (gfele_t *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgsrc = pgsrc + bgfsize;
                }
                pgdes = pgdes + pgfsize;
            }
            pgsrc = (gfele_t *)(psrc + times*packet_size);
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val != 0){
                    gfs->region_mul(pgdes, pgsrc, val, rest_size, 1);   
                }
                pgsrc = pgsrc + bgfsize;
            }
            pgdes = pgdes + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}

int mcoding_dpg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;
   
    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        pgsrc = (gfele_t *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (gfele_t *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgdes = pgdes + bgfsize;
                }
                pgsrc = pgsrc + pgfsize;
            }
        } 
    }else{
        pgsrc = (gfele_t *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (gfele_t *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    }
                    pgdes = pgdes + bgfsize;
                }
                pgsrc = pgsrc + pgfsize;
            }
            pgdes = (gfele_t *)(pdes+ times*packet_size);
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val != 0){
                    gfs->region_mul(pgdes, pgsrc, val, rest_size, 1);   
                }
                pgdes = pgdes + bgfsize;
            }
            pgsrc = pgsrc + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}

int mcoding_dbg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);
    
    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgsrc = pgsrc+pgfsize;
                    pgdes = pgdes+pgfsize;
                }
            }
        }
    }else{
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfs->region_mul(pgdes, pgsrc, val, packet_size, 1);
                    pgsrc = pgsrc+pgfsize;
                    pgdes = pgdes+pgfsize;
                }
                gfs->region_mul(pgdes, pgsrc, val, rest_size, 1);
            }
        }
    }

    return 1;
}


int mcoding_pbg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    gfele_t val;
    unsigned char  *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (unsigned char *)(psrc + j*block_size);
                pgdes = (unsigned char *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    pgdes = pgdes + packet_size;
                    pgsrc = pgsrc + packet_size;
                }
            }
        }
    }else{
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (unsigned char *)(psrc + j*block_size);
                pgdes = (unsigned char *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    pgdes = pgdes + packet_size;
                    pgsrc = pgsrc + packet_size;
                }
                gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, rest_size, 1);
            }
        }
    }
    return 1;
}

int mcoding_ppg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    gfele_t val;
    unsigned char *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;

    memset(pdes, 0, row*block_size);

    rest_size = block_size - times*packet_size;
    if(rest_size == 0){
        pgdes = (unsigned char *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (unsigned char *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val == 0)    continue;
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    pgsrc = pgsrc + block_size;
                }
                pgdes = pgdes + packet_size;
            }
        }
    }else{
        pgdes = (unsigned char *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (unsigned char *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val == 0)    continue;
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    pgsrc = pgsrc + block_size;
                }
                pgdes = pgdes + packet_size;
            }
            pgsrc = (unsigned char *)(psrc + times*packet_size);
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, rest_size, 1);
                pgsrc = pgsrc + block_size;
            }
            pgdes = pgdes + rest_size;
        }
    }

    return 1;

}

int mcoding_dpg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    gfele_t val;
    unsigned char *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    rest_size = block_size - times*packet_size;
   
    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        pgsrc = (unsigned char *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (unsigned char *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    }
                    pgdes = pgdes + block_size;
                }
                pgsrc = pgsrc + packet_size;
            }
        } 
    }else{
        pgsrc = (unsigned char *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (unsigned char *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val != 0){
                        gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    }
                    pgdes = pgdes + block_size;
                }
                pgsrc = pgsrc + packet_size;
            }
            pgdes = (unsigned char *)(pdes+ times*packet_size);
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0){
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, rest_size, 1);
                }
                pgdes = pgdes + block_size;
            }
            pgsrc = pgsrc + rest_size/sizeof(gfele_t);
        }
    }

    return 1;

}

int mcoding_dbg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    gfele_t val;
    unsigned char *pgdes, *pgsrc;

    assert(block_size >= packet_size);
    
    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (unsigned char *)(psrc + j*block_size);
                pgdes = (unsigned char *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    pgsrc = pgsrc+packet_size;
                    pgdes = pgdes+packet_size;
                }
            }
        }
    }else{
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0)    continue;
                pgsrc = (unsigned char *)(psrc + j*block_size);
                pgdes = (unsigned char *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, packet_size, 1);
                    pgsrc = pgsrc+packet_size;
                    pgdes = pgdes+packet_size;
                }
                gfc->multiply_region.w32(gfc, pgsrc, pgdes, val, rest_size, 1);
            }
        }
    }

    return 1;

}

static inline
void init_hindex(int *hindex, gfmat_t *pmat){
    int i, j;
    int h_tmp;
    gfele_t val;

    for(i = 0 ; i < pmat->col; i++){
        hindex[i] = 0; 
        for(j = 0; j < pmat->row; j++){
            val = pmat->data[j*(pmat->col)+i];
            h_tmp=0;
            while(val > 0){
                val >>= 1;
                ++h_tmp;
            }    
            hindex[i] = MAX(hindex[i], h_tmp);
        }    
    }
}

// TODO: optimize M2 -> do{}while
int mcoding_dpg_ss(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    gfele_t val;
    unsigned char *ppdes, *ppsrc, *pcom;
    int *hindex;
    int shift;
    gfele_t mask;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    rest_size = block_size - times*packet_size;

    hindex = (int *)malloc(col*sizeof(int));
    init_hindex(hindex, pmat);
    pcom = (unsigned char *)malloc(packet_size);

    memset(pdes, 0, row*block_size);
   
    if(rest_size == 0){
        ppsrc = psrc;
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                memcpy(pcom, ppsrc, packet_size);
                for(shift = 0, mask = 1; shift < hindex[j]; ++shift, mask<<=1){
                    ppdes = pdes + k*packet_size;
                    for(i = 0; i < row; ++i){
                        val = pmat->data[i*col+j];
                        if(val&mask){
                            //regionxor
                            region_xor(ppdes, pcom, packet_size);
                        }
                        ppdes = ppdes + block_size;
                    }
                    gfs->region_mul2((gfele_t *)pcom, packet_size);
                    //region_mul_2_64_w8((gfele_t *)pcom, packet_size);
                    //region_shift_mul_w8(pcom, pcom, 2, packet_size, 0);
                }
                ppsrc = ppsrc + packet_size;
            }
        }
    }else{
        ppsrc = psrc;
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                memcpy(pcom, ppsrc, packet_size);
                for(shift = 0, mask = 1; shift < hindex[j]; ++shift, mask<<=1){
                    ppdes = pdes + k*packet_size;
                    for(i = 0; i < row; ++i){
                        val = pmat->data[i*col+j];
                        if(val&mask){
                            //regionxor
                            region_xor(ppdes, pcom, packet_size);
                        }
                        ppdes = ppdes + block_size;
                    }
                    gfs->region_mul2((gfele_t *)pcom, packet_size);
                    //region_mul_2_64_w8((gfele_t *)pcom, packet_size);
                    //region_shift_mul_w8(pcom, pcom, 2, packet_size, 0);
                }
                ppsrc = ppsrc + packet_size;
            }
            memcpy(pcom, ppsrc, rest_size);
            for(shift = 0, mask = 1; shift < hindex[j]; ++shift, mask<<=1){
                ppdes = pdes+ times*packet_size;
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val&mask){
                        //regionxor
                        region_xor(ppdes, pcom, rest_size);
                    }
                    ppdes = ppdes + block_size;
                }
                gfs->region_mul2((gfele_t *)pcom, rest_size);
                //region_mul_2_64_w8((gfele_t *)pcom, rest_size);
                //region_shift_mul_w8(pcom, pcom, 2, rest_size, 0);
            }
            ppsrc = ppsrc + rest_size;
        }
    }

    free(pcom);
    free(hindex);
    return 1;
}




/*
 * XOR coding
*/
 

int mxcoding_dg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat){
    int i, j;
    int row, col;
    int bgfsize;
    gfele_t *pgdes, *pgsrc;
    gfele_t val;

    row = pmat->row;
    col = pmat->col;
    bgfsize = block_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    pgsrc = (gfele_t *)psrc;
    for(j = 0; j < col; ++j){
        pgdes = (gfele_t *)pdes;
        for(i = 0; i < row; ++i){
            val = pmat->data[i*col+j];
            if(val == 1){
                region_xor(pgdes, pgsrc, block_size);
            }
            pgdes = pgdes + bgfsize;
        }
        pgsrc = pgsrc + bgfsize;
    }

    return 1;
}

int mxcoding_pg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat){
    int i, j;
    int row, col;
    int bgfsize;
    gfele_t *pgdes, *pgsrc;
    gfele_t val;

    row = pmat->row;
    col = pmat->col;
    bgfsize = block_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    pgdes = (gfele_t *)pdes;
    for(i = 0; i < row; ++i){
        pgsrc = (gfele_t *)psrc;
        for(j = 0; j < col; ++j){
            val = pmat->data[i*col+j];
            if(val == 1){
                region_xor(pgdes, pgsrc, block_size);
            }
            pgsrc = pgsrc + bgfsize;
        }
        pgdes = pgdes + bgfsize;
    }

    return 1;
}

int mxcoding_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    memset(pdes, 0, row*block_size);

    rest_size = block_size - times*packet_size;
    if(rest_size == 0){
        pgdes = (gfele_t *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (gfele_t *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val == 1){
                        region_xor(pgdes, pgsrc, packet_size);
                    }
                    pgsrc = pgsrc + bgfsize;
                }
                pgdes = pgdes + pgfsize;
            }
        }
    }else{
        pgdes = (gfele_t *)(pdes);
        for(i = 0; i < row; ++i){
            for(k = 0; k < times; ++k){
                pgsrc = (gfele_t *)(psrc + k*packet_size);
                for(j = 0; j < col; ++j){
                    val = pmat->data[i*col+j];
                    if(val == 1){
                        region_xor(pgdes, pgsrc, packet_size);
                    }
                    pgsrc = pgsrc + bgfsize;
                }
                pgdes = pgdes + pgfsize;
            }
            pgsrc = (gfele_t *)(psrc + times*packet_size);
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 1){
                    region_xor(pgdes, pgsrc, rest_size);
                }
                pgsrc = pgsrc + bgfsize;
            }
            pgdes = pgdes + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}

int mxcoding_dpg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;
   
    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        pgsrc = (gfele_t *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (gfele_t *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val == 1){
                        region_xor(pgdes, pgsrc, packet_size);
                    }
                    pgdes = pgdes + bgfsize;
                }
                pgsrc = pgsrc + pgfsize;
            }
        } 
    }else{
        pgsrc = (gfele_t *)(psrc);
        for(j = 0; j < col; ++j){
            for(k = 0; k < times; ++k){
                pgdes = (gfele_t *)(pdes + k*packet_size);
                for(i = 0; i < row; ++i){
                    val = pmat->data[i*col+j];
                    if(val == 1){
                        region_xor(pgdes, pgsrc, packet_size);
                    }
                    pgdes = pgdes + bgfsize;
                }
                pgsrc = pgsrc + pgfsize;
            }
            pgdes = (gfele_t *)(pdes+ times*packet_size);
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 1){
                    region_xor(pgdes, pgsrc, rest_size);
                }
                pgdes = pgdes + bgfsize;
            }
            pgsrc = pgsrc + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}

int mxcoding_pbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0) continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    region_xor(pgdes, pgsrc, packet_size);
                    pgdes = pgdes + pgfsize;
                    pgsrc = pgsrc + pgfsize;
                }
            }
        }
    }else{
        for(i = 0; i < row; ++i){
            for(j = 0; j < col; ++j){
                val = pmat->data[i*col+j];
                if(val == 0) continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    region_xor(pgdes, pgsrc, packet_size);
                    pgdes = pgdes + pgfsize;
                    pgsrc = pgsrc + pgfsize;
                }
                region_xor(pgdes, pgsrc, rest_size);
            }
        }
    }
    return 1;
}

int mxcoding_dbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat){
    int row, col;
    int i, j, k;
    int times;
    int rest_size;
    int pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    row = pmat->row;
    col = pmat->col;
    times = block_size/packet_size;
    pgfsize = packet_size/sizeof(gfele_t);

    rest_size = block_size - times*packet_size;

    memset(pdes, 0, row*block_size);

    if(rest_size == 0){
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0) continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    region_xor(pgdes, pgsrc, packet_size);
                    pgsrc = pgsrc+pgfsize;
                    pgdes = pgdes+pgfsize;
                }
            }
        }
    }else{
        for(j = 0; j < col; ++j){
            for(i = 0; i < row; ++i){
                val = pmat->data[i*col+j];
                if(val == 0) continue;
                pgsrc = (gfele_t *)(psrc + j*block_size);
                pgdes = (gfele_t *)(pdes + i*block_size);
                for(k = 0; k < times; ++k){
                    region_xor(pgdes, pgsrc, packet_size);
                    pgsrc = pgsrc+pgfsize;
                    pgdes = pgdes+pgfsize;
                }
                region_xor(pgdes, pgsrc, rest_size);
            }
        }
    }

    return 1;
}

/*
 ******************* lil **********************
 */

int mxcoding_lil_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, lil_t *pzlil, int m, int k){
    int row, col;
    int i, j, p;
    int times;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;
    (void)m;
    (void)k;

    assert(block_size >= packet_size);

    //row = ZLIL_ROW(m, k);
    //col = ZLIL_COL(m, k);
    row = pzlil->row;
    col = pzlil->col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);

    memset(pdes, 0, row*((size_t)block_size));

    rest_size = block_size - times*packet_size;
    
    if(rest_size == 0){
        pgdes = (gfele_t *)pdes;
        pgsrc = (gfele_t *)psrc;
        for(i = 0; i < row; ++i){
            for(p = 0; p < times; ++p){
                for(j = 0; j < col; ++j){
                    val = (gfele_t)pzlil->data[i*col+j];
                    region_xor(pgdes, pgsrc+val*bgfsize+p*pgfsize, packet_size);
                }
                pgdes = pgdes + pgfsize;
            }
        }
    }else{
        pgdes = (gfele_t *)pdes;
        for(i = 0; i < row; ++i){
            for(p = 0; p < times; ++p){
                pgsrc = (gfele_t *)(psrc + p*packet_size);
                for(j = 0; j < col; ++j){
                    val = (gfele_t)pzlil->data[i*col+j];
                    region_xor(pgdes, pgsrc+val*bgfsize, packet_size);
                }
                pgdes = pgdes + pgfsize;
            }
            pgsrc = (gfele_t *)(psrc+times*packet_size);
            for(j = 0; j < col; ++j){
                val = (gfele_t)pzlil->data[i*col+j];
                region_xor(pgdes, pgsrc+val*bgfsize, rest_size);
            }
            pgdes = pgdes + rest_size/sizeof(gfele_t);
        }
    
    }

    return 1;
}

int mcoding_coomat_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, coomat_t *pzcoomat, int m, int k, gf_t *pgf){
    int row, col;
    int i, j, p;
    int times;
    int col_idx;
    int rest_size;
    int bgfsize, pgfsize;
    gfele_t val;
    gfele_t *pgdes, *pgsrc;

    assert(block_size >= packet_size);

    //row = ZLIL_ROW(m, k);
    //col = ZLIL_COL(m, k);
    row = pzcoomat->lil_pos.row;
    col = pzcoomat->lil_pos.col;
    times = block_size/packet_size;
    bgfsize = block_size/sizeof(gfele_t);
    pgfsize = packet_size/sizeof(gfele_t);
    (void)m;
    (void)k;

    memset(pdes, 0, row*((size_t)block_size));

    rest_size = block_size - times*packet_size;

    if(rest_size == 0){
        pgdes = (gfele_t *)pdes;
        for(i = 0; i < row; ++i){
            for(p = 0; p < times; ++p){
                pgsrc = (gfele_t *)(psrc+p*packet_size);
                for(j = 0; j < col; ++j){
                    col_idx = pzcoomat->lil_pos.data[i*col+j];
                    val = pzcoomat->mat_val.data[i*col+j];
                    pgf->multiply_region.w32(pgf, pgsrc+col_idx*bgfsize, pgdes, val, packet_size, 1);
                }
                pgdes = pgdes + pgfsize;
            }
        }
    }else{
        pgdes = (gfele_t *)pdes;
        //pgsrc = (gfele_t *)psrc;
        for(i = 0; i < row; ++i){
            for(p = 0; p < times; ++p){
                pgsrc = (gfele_t *)(psrc+p*packet_size);
                for(j = 0; j < col; ++j){
                    col_idx = pzcoomat->lil_pos.data[i*col+j];
                    val = pzcoomat->mat_val.data[i*col+j];
                    pgf->multiply_region.w32(pgf, pgsrc+col_idx*bgfsize, pgdes, val, packet_size, 1);
                    //pgf->multiply_region.w32(pgf, pgsrc+col_idx*bgfsize+p*pgfsize, pgdes, val, packet_size, 1);
                }
                pgdes = pgdes + pgfsize;
            }
            pgsrc = (gfele_t *)(psrc+times*packet_size);
            for(j = 0; j < col; ++j){
                col_idx = pzcoomat->lil_pos.data[i*col+j];
                val = pzcoomat->mat_val.data[i*col+j];
                pgf->multiply_region.w32(pgf, pgsrc+col_idx*bgfsize, pgdes, val, rest_size, 1);
            }
            pgdes = pgdes + rest_size/sizeof(gfele_t);
        }
    }

    return 1;
}
