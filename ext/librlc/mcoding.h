#ifndef MCODING_H
#define MCODING_H
#include "mat.h"
#include "zcode_struct.h"
#include "gfshift.h"
#include "gf_complete.h"

#define MAX(a,b) (((a)>(b))?(a):(b))

int get_block_size(int file_size, gfmat_t *pmat);
int get_block_size_by_col(int file_size, int col);

/*
 * RS coding
 */
int mcoding_dg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat, gfm_t *gf);
int mcoding_pg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat, gfm_t *gf);

int mcoding_pbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf);
int mcoding_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf);
int mcoding_dpg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf);
int mcoding_dbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfm_t *gf);

int mcoding_pbg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs);
int mcoding_ppg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs);
int mcoding_dpg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs);
int mcoding_dbg_s(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs);

int mcoding_pbg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc);
int mcoding_ppg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc);
int mcoding_dpg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc);
int mcoding_dbg_f(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gf_t *gfc);

// ss means 'shift-and-add' and sheduled
int mcoding_dpg_ss(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat, gfs_t *gfs);


/*
 * XOR coding
 */
int mxcoding_dg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat);
int mxcoding_pg(unsigned char *pdes, unsigned char *psrc, int block_size, gfmat_t *pmat);

int mxcoding_pbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat);
int mxcoding_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat);
int mxcoding_dbg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat);
int mxcoding_dpg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, gfmat_t *pmat);

/*
 * lil coing
 */
int mxcoding_lil_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, lil_t *pzlil, int m, int k);
int mcoding_coomat_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, coomat_t *pzcoomat, int m, int k, gf_t *pgf);
/*int mcoding_rslil_ppg(unsigned char *pdes, unsigned char *psrc, int block_size, int packet_size, coomat_t *pzcoomat, int m, int k, gf_t *pgf);*/
#endif
