#include "galois.h"
#include "region_xor.h"

#define NONE (10)
#define TABLE (11)
#define SHIFT (12)
#define LOGS (13)
#define SPLITW8 (14)

int gfw;    // 2^gfw equals to the size of the field
int NW, NWM;

gfele_t *log_table[33] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};
gfele_t *ilog_table[33] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};

gfele_t *mult_table[33] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
		NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};

gfele_t *div_table[33] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
	    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};

gfele_t *split_table_w8[7] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL};


static int prim_poly[33] = 
{ 0, 
/*  1 */     1, 
/*  2 */    07,
/*  3 */    013,
/*  4 */    023,
/*  5 */    045,
/*  6 */    0103,
/*  7 */    0211,
/*  8 */    0435,
/*  9 */    01021,
/* 10 */    02011,
/* 11 */    04005,
/* 12 */    010123,
/* 13 */    020033,
/* 14 */    042103,
/* 15 */    0100003,
/* 16 */    0210013,
/* 17 */    0400011,
/* 18 */    01000201,
/* 19 */    02000047,
/* 20 */    04000011,
/* 21 */    010000005,
/* 22 */    020000003,
/* 23 */    040000041,
/* 24 */    0100000207,
/* 25 */    0200000011,
/* 26 */    0400000107,
/* 27 */    01000000047,
/* 28 */    02000000011,
/* 29 */    04000000005,
/* 30 */    010040000007,
/* 31 */    020000000011, 
/* 32 */    00020000007 };  /* Really 40020000007, but we're omitting the high order bit */

static int mult_type[33] = 
{ NONE, 
/*  1 */   TABLE, 
/*  2 */   TABLE,
/*  3 */   TABLE,
/*  4 */   TABLE,
/*  5 */   TABLE,
/*  6 */   TABLE,
/*  7 */   TABLE,
/*  8 */   TABLE,
/*  9 */   TABLE,
/* 10 */   LOGS,
/* 11 */   LOGS,
/* 12 */   LOGS,
/* 13 */   LOGS,
/* 14 */   LOGS,
/* 15 */   LOGS,
/* 16 */   LOGS,
/* 17 */   LOGS,
/* 18 */   LOGS,
/* 19 */   LOGS,
/* 20 */   LOGS,
/* 21 */   LOGS,
/* 22 */   LOGS,
/* 23 */   SHIFT,
/* 24 */   SHIFT,
/* 25 */   SHIFT,
/* 26 */   SHIFT,
/* 27 */   SHIFT,
/* 28 */   SHIFT,
/* 29 */   SHIFT,
/* 30 */   SHIFT,
/* 31 */   SHIFT,
/* 32 */   SPLITW8 };

gfele_t galois_create_mult_tables(int ww) {
	int nw = 1 << ww;
	int x, y;
	gfele_t logx;
	int j;
	if(ww >= 14) {
		return 0;
	}

	if(mult_table[ww] != NULL) {
		return 1;
	}
	if((mult_table[ww] = (gfele_t *) malloc (sizeof(gfele_t) * nw * nw))==NULL){
		printf("Fail to malloc memory for mult_table!\n");
		exit(0);
	}
	if(mult_table[ww] == NULL) return 0;
	
	if((div_table[ww] = (gfele_t *) malloc (sizeof(gfele_t) * nw * nw))==NULL){
		printf("Fail to malloc memory for div_table!\n");
		exit(0);
	}
	if(div_table[ww] == NULL) {
		free(div_table[ww]);
		mult_table[ww] = NULL;
		return 0;
	}
	if(log_table[ww] == NULL) {
		if(galois_create_log_tables(ww) < 1) {
			free(mult_table[ww]);
			free(div_table[ww]);
			mult_table[ww] = NULL;
			div_table[ww] = NULL;
			return 0;
		}
	}
	//x = 0, set table_value
	j = 0;
	mult_table[ww][j] = 0;
	div_table[ww][j] = 0;
	++j;
	for(y = 1; y < nw; ++y) {
		mult_table[ww][j] = 0;
		div_table[ww][j] = 0;
		++j;
	}
	for(x = 1; x < nw; ++x) {
		mult_table[ww][j] = 0;
		div_table[ww][j] = 0;
		++j;
		logx = log_table[ww][x];
		for(y = 1; y < nw; ++y) {
			mult_table[ww][j] = ilog_table[ww][logx + log_table[ww][y]];
			div_table[ww][j] = ilog_table[ww][(int)(logx - log_table[ww][y])];
			++j;
		}
	}
	return 1;
}

gfele_t galois_create_log_tables(int ww) {
	int nw = 1 << ww;
	int nwm = nw - 1;
	int b;
	int j;
	if(ww > 30) {
		return 0;
	}
	if(log_table[ww] != NULL) return 1;
	if((log_table[ww] = (gfele_t *) malloc (sizeof(gfele_t) * nw)) == NULL){
		printf("Fail to malloc memory for log_table!\n");
		exit(0);
	};
	if(log_table[ww] == NULL) return 0;

	if((ilog_table[ww] = (gfele_t *) malloc (sizeof(gfele_t) * nw * 3)) == NULL){
		printf("Fail to malloc memory for ilog_table!\n");
		exit(0);
	}
	if(ilog_table[ww] == NULL) {
		free(ilog_table[ww]);
		log_table[ww] = NULL;
		return 0;
	}

	for(j = 0; j < nw; ++j) {
		log_table[ww][j] = nwm;
		ilog_table[ww][j] = 0;
	}

	b = 1;
	for(j = 0; j < nwm; ++j) {
		if(log_table[ww][b] != (unsigned)nwm) {
			printf("%d %d\n", nwm, log_table[ww][b]);
			fprintf(stderr, "galois_create_log_tables error - in galois_create_log tables() func\n");
			exit(0);
		}
		log_table[ww][b] = j;
		ilog_table[ww][j] = b;
		b = b << 1;
		if(b & nw) {
			b = (b ^ prim_poly[ww]) & nwm;
		}
	}
	for(j = 0; j < nwm; ++j) {
		ilog_table[ww][j + nwm] = ilog_table[ww][j];
		ilog_table[ww][j + nwm * 2] = ilog_table[ww][j];
	}
	ilog_table[ww] += nwm;
	return 1;
}

gfele_t galois_create_split_w8_tables() {
	int p1, p2, i, j, p1elt, p2elt, index, ishift, jshift;
    gfele_t *table;
	if(split_table_w8[0] != NULL) return 1;
	if(galois_create_mult_tables(8) < 1) return 0;

	for(i = 0; i < 7; ++i) {
		if((split_table_w8[i] = (gfele_t *) malloc (sizeof(gfele_t) * (1 << 16)))==NULL){
			printf("Fail to malloc memory for split_table!\n");
			exit(0);
		}
		if(split_table_w8[i] == NULL) {
			for(i--; i >= 0; --i) {
				free(split_table_w8[i]);
			}
			return 0;
		}
	}
	for(i = 0; i < 4; i += 3) {
		ishift = i * 8;
		for(j = ((i == 0)? 0 : 1); j < 4; ++j) {
			jshift = j * 8;
			table = split_table_w8[i + j];
			index = 0;
			for(p1 = 0; p1 < 256; ++p1) {
				p1elt = (p1 << ishift);
				for(p2 = 0; p2 < 256; ++p2) {
					p2elt = (p2 << jshift);
					table[index] = galois_shift_multiply(p1elt, p2elt);
					++index;
				}
			}
		}
	}
	return 1;
}

gfele_t single_mul_t(gfele_t a, gfele_t b) {
	if(a == 0 || b == 0) {
		return 0;
	}
	return mult_table[gfw][((int)a << gfw) | b];
}

gfele_t single_div_t(gfele_t a, gfele_t b) {
	return div_table[gfw][(int)(a << gfw) | b];
}

gfele_t single_inv_t(gfele_t a) {
	if(a == 0) return 0;
	return single_div_t(1, a);
}


gfele_t single_mul_l(gfele_t a, gfele_t b) {
	if(a == 0 || b == 0) {
		return 0;
	}
	return ilog_table[gfw][log_table[gfw][a] + log_table[gfw][b]];
}

gfele_t single_div_l(gfele_t a, gfele_t b) {
	if(b == 0) return 0;
	if(a == 0) return 0;
	return ilog_table[gfw][(int)(log_table[gfw][a] - log_table[gfw][b])];
}

gfele_t single_inv_l(gfele_t a) {
	if(a == 0) return 0;
	return single_div_l(1, a);
}

gfele_t single_mul_s(gfele_t a, gfele_t b) {
	if(a == 0 || b == 0) {
		return 0;
	} 
	return galois_shift_multiply(a, b);
}

gfele_t single_div_s(gfele_t a, gfele_t b) {
	if(b == 0) return 0;
	if(a == 0) return 0;
	return single_mul_s(a, galois_shift_inverse(b));
}

gfele_t single_inv_s(gfele_t a) {
	if(a == 0) return 0;
	return galois_shift_inverse(a);
}

gfele_t single_mul_split(gfele_t a, gfele_t b) {
	if(a == 0 || b == 0) {
		return 0;
	}
	return split_table_w8_multiply(a, b);
}

gfele_t single_div_split(gfele_t a, gfele_t b) {
	if(b == 0) return 0;
	if(a == 0) return 0;
	return single_mul_split(a, galois_shift_inverse(b));
}



gfele_t galois_log(gfele_t value) {
	if(log_table[gfw] == NULL) {
		if(galois_create_log_tables(gfw) < 1) {
			fprintf(stderr, "Error: galois_log - w is too big - in galois_log() func\n");
			exit(0);
		}
	}
	return log_table[gfw][value];
}

gfele_t galois_ilog(gfele_t value) {
	if(ilog_table[gfw] == NULL) {
		if(galois_create_log_tables(gfw) < 1) {
			fprintf(stderr, "Error: galois_ilog -w is too big. - in galois_ilog() func\n");
			exit(0);
		}
	}
	return ilog_table[gfw][value];
}


gfele_t galois_shift_multiply(gfele_t x, gfele_t y) {
	gfele_t prod;
	gfele_t j, ind;
	gfele_t scratch[33];
    int i, k;

	prod = 0;
	for(i = 0; i < gfw; ++i) {
		scratch[i] = y;
		if(y & (1 << (gfw - 1))) {
			y = y << 1;
			y = (y ^ prim_poly[gfw]) & NWM;
		} else {
			y = y << 1;
		}
	}
	for(i = 0; i < gfw; ++i) {
		ind = (1 << i);
		if(ind & x) {
			j = 1;
			for(k = 0; k < gfw; ++k) {
				prod = prod ^ (j & scratch[i]);
				j = (j << 1);
			}
		}
	}
	return prod;
}

static
void galois_invert_binary_matrix(int *mat, int *inv, gfele_t row_w) {
	int cols, rows, i, j;
    int tmp;

	cols = rows = row_w;

	for (i = 0; i < rows; i++) inv[i] = (1 << i);

	/* First -- convert into upper triangular */

	for (i = 0; i < cols; i++) {

	/* Swap rows if we ave a zero i,i element.  If we can't swap, then the 
	    matrix was not invertible */

		if ((mat[i] & (1 << i)) == 0) {
			for (j = i+1; j < rows && (mat[j] & (1 << i)) == 0; j++) ;
			if (j == rows) {
				fprintf(stderr, "galois_invert_matrix: Matrix not invertible!!\n");
				exit(1);
			}
				tmp = mat[i]; mat[i] = mat[j]; mat[j] = tmp;
				tmp = inv[i]; inv[i] = inv[j]; inv[j] = tmp;
		}

		/* Now for each j>i, add A_ji*Ai to Aj */
		for (j = i+1; j != rows; j++) {
			if ((mat[j] & (1 << i)) != 0) {
				mat[j] ^= mat[i];
				inv[j] ^= inv[i];
			}
		}
	}
  /* Now the matrix is upper triangular.  Start at the top and multiply down */

	for (i = rows-1; i >= 0; i--) {
		for (j = 0; j < i; j++) {
			if (mat[j] & (1 << i)) {
/*        mat[j] ^= mat[i]; */
				inv[j] ^= inv[i];
			}
		}
						  
	}
}


gfele_t galois_shift_inverse(gfele_t y) {
	int mat2[32];
	int inv2[32];
	int i;
	int nw = 1 << (gfw - 1);

	int yy = y;

	for (i = 0; i < gfw; i++) {
		mat2[i] = yy;

		if (yy & nw) {
			yy = yy << 1;
			yy = (yy ^ prim_poly[gfw]) & NWM;
		} else {
			yy = yy << 1;
		}
	}

	galois_invert_binary_matrix(mat2, inv2, gfw);

	return inv2[0];
}

gfele_t split_table_w8_multiply(gfele_t x, gfele_t y) {
	int i, j, a, b, accum, i8, j8;
	accum = 0;
	i8 = 0;
	for(i = 0; i < 4; ++i) {
		a = ((x >> i8) & 255) << 8;
		j8 = 0;
		for(j = 0; j < 4; ++j) {
			b = ((y >> j8) & 255);
			accum ^= split_table_w8[i + j][a | b];
			j8 += 8;
		}
		i8 += 8;
	}
	return accum;
}

int region_mul_wt(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    gfele_t *rdes;
    gfele_t *rsrc;
    int i;
    int hindex;
    int tlen;

    assert(mult_table[gfw] != NULL);   

    rdes = des;
    rsrc = src;
    tlen = len/sizeof(gfele_t);

    if(multipler == 0){
        if(ifxor == 0 ){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if(multipler == 1){
        if(ifxor == 0){
            memcpy(rdes, rsrc, len);
            return 1;
        }else{
            region_xor_8(des, src, len);
            return 1;
        }
    }

    hindex = multipler * NW;
    if(ifxor == 0){
        for(i = 0; i < tlen; ++i){
            rdes[i] = mult_table[gfw][hindex + rsrc[i]];
        }
    }else{
        for(i = 0; i < tlen; ++i){
            rdes[i] ^= mult_table[gfw][hindex + rsrc[i]];
        }
    }

    return 1;
}

int region_mul_wl(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    gfele_t *rdes;
    gfele_t *rsrc;
    int i;
    int log_m;
    int llen;

    assert(log_table[gfw] != NULL);   
    assert(ilog_table[gfw] != NULL);   

    rdes = des;
    rsrc = src;
    llen = len/sizeof(gfele_t);

    if(multipler == 0){
        if(ifxor == 0 ){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if(multipler == 1){
        if(ifxor == 0){
            memcpy(rdes, rsrc, len);
            return 1;
        }else{
            region_xor_8(des, src, len);
            return 1;
        }
    }

    log_m = log_table[gfw][multipler];
    if(ifxor == 0){
        for(i = 0; i < llen; ++i){
            rdes[i] = ilog_table[16][log_table[16][rsrc[i]] + log_m];
        }
    }else{
        for(i = 0; i < llen; ++i){
            rdes[i] ^= ilog_table[16][log_table[16][rsrc[i]] + log_m];
        }
    }

    return 1;
}

int region_mul_wf(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    gfele_t *rdes;
    gfele_t *rsrc;
    gfele_t *rmid;
    int i, j;
    int mbits[33];
    gfele_t val = multipler;
    gfele_t hmask = 1 << (gfw-1);

    rdes = des;
    rsrc = src;
    
    if(multipler == 0){
        if(ifxor == 0){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if(multipler == 1){
        if(ifxor == 0){
            memcpy(rdes, rsrc, len);
            return 1;
        }else{
            region_xor_8(des, src, len);
            return 1;
        }
    }

    rmid = (gfele_t *)malloc(len);
    for(i  = 0; i < gfw; ++i){
        if((1<<i)&val){
            mbits[i] = 1;
        }else{
            mbits[i] = 0;
        }
    }
    {
        for(i = gfw-1; i >= 0; --i){
            if(mbits[i] == 1) break;
        }
        memcpy(rmid, rsrc, len);
        --i;
        while(i >= 0){
            for(j = 0; j < (int)(len/sizeof(gfele_t)); ++j){
                val = rmid[j];
                if(val & hmask){
                    rmid[j] = (val<<1)^prim_poly[gfw];
                }else{
                    rmid[j] = val<<1;
                }
            }
            if(mbits[i] == 1){
                region_xor_8(rmid, rsrc, len);
            }
            --i;
        }
    }
    
    if(ifxor == 0){
        memcpy(rdes, rmid, len);
    }else{
        region_xor_8(rdes, rmid, len);
    }
    
    free(rmid);
    return 1;
}

int region_mul_w4(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    uint8_t *rdes;
    uint8_t *rsrc;
    int hindex;
    uint8_t mask1 = 0xf0;
    uint8_t mask2 = 0x0f;
    int i;

    assert(mult_table[4]!=NULL);
    
    hindex = multipler<<4;
    rdes = (uint8_t *)des;
    rsrc = (uint8_t *)src;


    if(multipler == 0){
        if(ifxor == 0 ){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if((multipler == 1)&&(ifxor == 0)){
        memcpy(rdes, rsrc, len);
        return 1;
    }
    if((multipler == 1)&&(ifxor != 0)){
        region_xor_8(des, src, len);
        return 1;
    }

    if(ifxor == 0){
        for(i = 0; i < len; ++i){
            rdes[i] = mult_table[4][hindex+(rsrc[i]&mask2)];
            rdes[i] ^= (mult_table[4][multipler+(rsrc[i]&mask1)]<<4);
        }
    }else{
        for(i = 0; i < len; ++i){
            rdes[i] ^= mult_table[4][hindex+(rsrc[i]&mask2)];
            rdes[i] ^= (mult_table[4][multipler+(rsrc[i]&mask1)]<<4);
        }
    }

    return len;
}

int region_mul_w8(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    uint8_t *rdes;
    uint8_t *rsrc;
    int i;
    int hindex;

    assert(mult_table[8]!=NULL);

    hindex = multipler * NW;
    rdes = (uint8_t *)des;
    rsrc = (uint8_t *)src;

    if(multipler == 0){
        if(ifxor == 0 ){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if((multipler == 1)&&(ifxor == 0)){
        memcpy(rdes, rsrc, len);
        return 1;
    }
    if((multipler == 1)&&(ifxor != 0)){
        region_xor_8(des, src, len);
        return 1;
    }
    if(multipler == 2){
        region_mul_2_w8(des, src, len, ifxor);
        return 1;
    }
    
    if(ifxor == 0){
        for(i = 0; i < len; ++i){
            rdes[i] = mult_table[8][hindex + rsrc[i]];
        }
    }else{
        for(i = 0; i < len; ++i){
            rdes[i] ^= mult_table[8][hindex + rsrc[i]];
        }
    }
    return 1;
}


int region_mul_w16(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    uint16_t *rdes;
    uint16_t *rsrc;
    uint16_t log_m;
    int i, len16;

    assert(log_table[16] != NULL);
    assert(ilog_table[16] != NULL);

    rdes = (uint16_t *)des;
    rsrc = (uint16_t *)src;

    if(multipler == 0){
        if(ifxor == 0 ){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if((multipler == 1)&&(ifxor == 0)){
        memcpy(rdes, rsrc, len);
        return 1;
    }
    if((multipler == 1)&&(ifxor != 0)){
        region_xor_8(des, src, len);
        return 1;
    }
    if(multipler == 2){
        region_mul_2_w16((gfele_t *)rdes, (gfele_t *)rsrc, len, ifxor);
        return 1;
    }
    
    log_m = log_table[16][multipler];
    len16 = len/sizeof(uint16_t);
    
    if(ifxor == 0){
        for(i = 0; i < len16; ++i){
            if(rsrc[i] == 0){
                rdes[i] = 0;
            }else{
                rdes[i] = ilog_table[16][log_table[16][rsrc[i]] + log_m];
            }
        }
    }else{
        for(i = 0; i < len16; ++i){
            if(rsrc[i] == 0){
                continue;
            }
            rdes[i] ^= ilog_table[16][log_table[16][rsrc[i]] + log_m];
        }
    }

    return 1;
}

int region_mul_w32(gfele_t *des, gfele_t *src, gfele_t multipler, int len, int ifxor){
    uint32_t *rdes;
    uint32_t *rsrc;
    uint32_t accum;
    int i; 
    int len32;
    int mp[4];
    int lindex;

    rdes = (uint32_t *)des;
    rsrc = (uint32_t *)src;

    assert(split_table_w8[0]!=NULL);

    if(multipler == 0){
        if(ifxor == 0 ){
            memset(rdes, 0, len);
        }
        return 1;
    }
    if((multipler == 1)&&(ifxor == 0)){
        memcpy(rdes, rsrc, len);
        return 1;
    }
    if((multipler == 1)&&(ifxor != 0)){
        region_xor_8(des, src, len);
        return 1;
    }
    if(multipler == 2){
        region_mul_2_w32((gfele_t *)rdes, (gfele_t *)rsrc, len, ifxor);
        return 1;
    }
    
    for(i = 0; i < 4; ++i){
        mp[i] = (((multipler>>(i*8))&255)<<8);
    }
    len32 = len/sizeof(uint32_t);

    if(!ifxor){
        for(i = 0; i < len32; ++i){
            accum = 0;
            
            lindex = (rsrc[i]&255);
            accum ^= split_table_w8[0][mp[0]|lindex];
            accum ^= split_table_w8[1][mp[1]|lindex];
            accum ^= split_table_w8[2][mp[2]|lindex];
            accum ^= split_table_w8[3][mp[3]|lindex];
            lindex = ((rsrc[i]>>8)&255);
            accum ^= split_table_w8[1][mp[0]|lindex];
            accum ^= split_table_w8[2][mp[1]|lindex];
            accum ^= split_table_w8[3][mp[2]|lindex];
            accum ^= split_table_w8[4][mp[3]|lindex];
            lindex = ((rsrc[i]>>16)&255);
            accum ^= split_table_w8[2][mp[0]|lindex];
            accum ^= split_table_w8[3][mp[1]|lindex];
            accum ^= split_table_w8[4][mp[2]|lindex];
            accum ^= split_table_w8[5][mp[3]|lindex];
            lindex = ((rsrc[i]>>24)&255);
            accum ^= split_table_w8[3][mp[0]|lindex];
            accum ^= split_table_w8[4][mp[1]|lindex];
            accum ^= split_table_w8[5][mp[2]|lindex];
            accum ^= split_table_w8[6][mp[3]|lindex];

            rdes[i] = accum;
        }
    }else{
        for(i = 0; i < len32; ++i){
            accum = 0;
            
            lindex = (rsrc[i]&255);
            accum ^= split_table_w8[0][mp[0]|lindex];
            accum ^= split_table_w8[1][mp[1]|lindex];
            accum ^= split_table_w8[2][mp[2]|lindex];
            accum ^= split_table_w8[3][mp[3]|lindex];
            lindex = ((rsrc[i]>>8)&255);
            accum ^= split_table_w8[1][mp[0]|lindex];
            accum ^= split_table_w8[2][mp[1]|lindex];
            accum ^= split_table_w8[3][mp[2]|lindex];
            accum ^= split_table_w8[4][mp[3]|lindex];
            lindex = ((rsrc[i]>>16)&255);
            accum ^= split_table_w8[2][mp[0]|lindex];
            accum ^= split_table_w8[3][mp[1]|lindex];
            accum ^= split_table_w8[4][mp[2]|lindex];
            accum ^= split_table_w8[5][mp[3]|lindex];
            lindex = ((rsrc[i]>>24)&255);
            accum ^= split_table_w8[3][mp[0]|lindex];
            accum ^= split_table_w8[4][mp[1]|lindex];
            accum ^= split_table_w8[5][mp[2]|lindex];
            accum ^= split_table_w8[6][mp[3]|lindex];

            rdes[i] ^= accum;
        }
    }

    return 1;
}

int region_mul_2_w8(gfele_t *des, gfele_t *src, int len, int ifxor){
    int i;
    uint8_t *rdes;
    uint8_t *rsrc;
    uint8_t mod8;
    
    rdes = (uint8_t *)des;
    rsrc = (uint8_t *)src;

    if(ifxor == 0){
        for(i = 0; i < len; ++i){
            mod8 = (rsrc[i]<<1)^((rsrc[i]&0x80)?prim_poly[8]:0);
            rdes[i] = mod8;
        }
    }else{
        for(i = 0; i < len; ++i){
            mod8 = (rsrc[i]<<1)^((rsrc[i]&0x80)?prim_poly[8]:0);
            rdes[i] ^= mod8;
        }
    }

    return 1;
}


int region_mul_2_w16(gfele_t *des, gfele_t *src, int len, int ifxor){
    int i;
    uint16_t *rdes;
    uint16_t *rsrc;
    uint16_t mod16;
    int len16;
    
    len16 = len/2;
    rdes = (uint16_t *)des;
    rsrc = (uint16_t *)src;

    if(ifxor == 0){
        for(i = 0; i < len16; ++i){
            mod16 = (rsrc[i]<<1)^((rsrc[i]&0x8000)?prim_poly[16]:0);
            rdes[i] = mod16;
        }
    }else{
        for(i = 0; i < len16; ++i){
            mod16 = (rsrc[i]<<1)^((rsrc[i]&0x8000)?prim_poly[16]:0);
            rdes[i] ^= mod16;
        }
    }

    return 1;
}

int region_mul_2_w32(gfele_t *des, gfele_t *src, int len, int ifxor){
    int i;
    uint32_t *rdes;
    uint32_t *rsrc;
    uint32_t mod32;
    int len32;
    
    len32 = len/4;
    rdes = (uint32_t *)des;
    rsrc = (uint32_t *)src;

    if(ifxor == 0){
        for(i = 0; i < len32; ++i){
            mod32 = (rsrc[i]<<1)^((rsrc[i]&0x80000000)?prim_poly[32]:0);
            rdes[i] = mod32;
        }
    }else{
        for(i = 0; i < len32; ++i){
            mod32 = (rsrc[i]<<1)^((rsrc[i]&0x80000000)?prim_poly[32]:0);
            rdes[i] ^= mod32;
        }
    }

    return 1;
}

int gf_init(gfm_t *gf, int w) {
	gfw = w;
    NW = 1 << gfw;
    NWM = (w == 32? (int)0xffffffff: (NW - 1));

    //region_mul
    switch(gfw) {
        case 4:
            gf->region_mul = region_mul_w4;
            break;
        case 8:
            gf->region_mul = region_mul_w8;
            break;
        case 16:
            gf->region_mul = region_mul_w16;
            break;
        case 32:
            gf->region_mul = region_mul_w32;
            break;
        default:
            gf->region_mul = NULL;
    }

    //single_mul
	switch(mult_type[gfw]) {
		case TABLE:
			if(mult_table[gfw] == NULL) {
				if(galois_create_mult_tables(gfw) < 1) {
					fprintf(stderr, "ERROR: cannot make multiplication table - in gf_init() func\n");
					exit(0);
				}
			}
			gf->mul = single_mul_t;
			gf->div = single_div_t;
			gf->inv = single_inv_t;
            if(gf->region_mul == NULL){
                gf->region_mul = region_mul_wt;
            }
			break;
		case LOGS:
			if(log_table[gfw] == NULL) {
				if(galois_create_log_tables(gfw) < 1) {
					fprintf(stderr, "ERROR: cannot make log tables - in gf_init() func\n");
					exit(0);
				}
			}
			gf->mul = single_mul_l;
			gf->div = single_div_l;
			gf->inv = single_inv_l;
            if(gf->region_mul == NULL){
                gf->region_mul = region_mul_wl;
            }
			break;
		case SHIFT:
			gf->mul = single_mul_s;
			gf->div = single_div_s;
			gf->inv = single_inv_s;
            if(gf->region_mul == NULL){
                gf->region_mul = region_mul_wf;
            }
			break;
		case SPLITW8:
			if(split_table_w8[0] == NULL) {
				if(galois_create_split_w8_tables() < 1) {
					fprintf(stderr, "ERROR: cannot make split_w8_tables - in gf_init() func\n");
					exit(0);
				}
			}
			gf->mul = single_mul_split;
			gf->div = single_div_split;
			gf->inv = single_inv_s;
            if(gf->region_mul == NULL){
				fprintf(stderr, "ERROR: region_mul shouldn't be nul - in gf_init() func\n");
				exit(0);
            }
			break;
		default: break;
	}
	return 1;
}

int gf_free(){
	int i;

	switch(mult_type[gfw]) {
		case TABLE:
			if(mult_table[gfw] != NULL) {
				free(mult_table[gfw]);
				mult_table[gfw] = NULL;
			}
			break;
		case LOGS:
			if(log_table[gfw] != NULL) {
				free(log_table[gfw]);
				log_table[gfw] = NULL;
				free((ilog_table[gfw]-NWM));
				ilog_table[gfw] = NULL;
			}
			break;
		case SHIFT:
			break;
		case SPLITW8:
			for(i =0; i < 7; ++i){
				if(split_table_w8[i] != NULL){
					free(split_table_w8[i]);
					split_table_w8[i] = NULL;
				}
			}
			break;
		default: break;
    }
    return 1;
}
