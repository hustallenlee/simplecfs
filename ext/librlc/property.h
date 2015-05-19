#pragma once
#include "mat.h"
#include "zcode_struct.h"

int rank(gfmat_t * pmat, gfm_t *gf);
int xrank(gfmat_t * pmat);

int invertible(gfmat_t * pmat, gfm_t *gf);

int mds_rs(gfmat_t *pmat, gfm_t *gf);

//minimum storage like F-MSR
int mds_msr(gfmat_t *pmat, int n,  gfm_t *gf);
int mds_msr_with_fnode(gfmat_t *pmat, int n, int fnode, gfm_t *gf);

int xmds_msr(gfmat_t *pmat,  int n);

//mds property for normal regenerating codes
int mds_rc(gfmat_t *pmat, int n, int k, gfm_t *gf);
int mds_rc_with_fnode(gfmat_t *pmat, int n, int k, int fnode, gfm_t *gf);

//coomat
int mds_coomat(coomat_t *pcmat, int n, gfm_t *gf);

//int rmds_msr(gfmat_t *pmat, int n, gfm_t *gf);
