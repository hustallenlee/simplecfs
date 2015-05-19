#include <inttypes.h>
#include <nmmintrin.h>
#include <emmintrin.h>
#include <immintrin.h>
#include "gfshift.h"

struct pw4c64{
    uint64_t prim;
    uint64_t mask1;
    uint64_t mask2;
} pw4c64 = {UINT64_C(0x3333333333333333), \
            UINT64_C(0xeeeeeeeeeeeeeeee), \
            UINT64_C(0x8888888888888888)};

struct pw8c64{
    uint64_t prim;
    uint64_t mask1;
    uint64_t mask2;
} pw8c64 = {UINT64_C(0x1d1d1d1d1d1d1d1d), \
            UINT64_C(0xfefefefefefefefe), \
            UINT64_C(0x8080808080808080)};

struct pw16c64{
    uint64_t prim;
    uint64_t mask1;
    uint64_t mask2;
} pw16c64={ UINT64_C(0x100b100b100b100b), \
            UINT64_C(0xfffefffefffefffe), \
            UINT64_C(0x8000800080008000)};

struct pw32c64{
    uint64_t prim;
    uint64_t mask1;
    uint64_t mask2;
} pw32c64={ UINT64_C(0x40000700400007), \
            UINT64_C(0xfffffffefffffffe), \
            UINT64_C(0x8000000080000000)};

struct gfprim{
    uint8_t w4;
    uint8_t w8;
    uint16_t w16;
    uint32_t w32;
} prim = {  0x3 , \
            0x1d , \
            0x100b, \
            0x400007};

int region_mul_2_64_w4(gfele_t *region, int len){
    uint64_t tmp, tmp2;
    uint64_t *pl, *ptop;

    assert(len%8 == 0);

    pl = (uint64_t *)region;
    ptop = pl + len/8;

    while(pl < ptop){
        tmp = ((*pl)<<1UL) & pw4c64.mask1;
        tmp2 = (*pl) & pw4c64.mask2;
        tmp2 = ((tmp2 << 1UL) - (tmp2 >> 3UL));
        *pl = (tmp ^ (tmp2 & pw4c64.prim));
        pl++;
    }

    return 1;
}

int region_mul_2_64_w8(gfele_t *region, int len){
    uint64_t tmp, tmp2;
    uint64_t *pl, *ptop;

    assert(len%8 == 0);

    pl = (uint64_t *)region;
    ptop = pl + len/8;

    while(pl < ptop){
        tmp = ((*pl)<<1UL) & pw8c64.mask1;
        tmp2 = (*pl) & pw8c64.mask2;
        tmp2 = ((tmp2 << 1UL) - (tmp2 >> 7UL));
        *pl = (tmp ^ (tmp2 & pw8c64.prim));
        pl++;
    }

    return 1;
}

int region_mul_2_64_w16(gfele_t *region, int len){
    uint64_t tmp, tmp2;
    uint64_t *pl, *ptop;

    assert(len%8 == 0);

    pl = (uint64_t *)region;
    ptop = pl + len/8;

    while(pl < ptop){
        tmp = ((*pl)<<1UL) & pw16c64.mask1;
        tmp2 = (*pl) & pw16c64.mask2;
        tmp2 = ((tmp2 << 1UL) - (tmp2 >> 15UL));
        *pl = (tmp ^ (tmp2 & pw16c64.prim));
        pl++;
    }

    return 1;
}

int region_mul_2_64_w32(gfele_t *region, int len){
    uint64_t tmp, tmp2;
    uint64_t *pl, *ptop;

    assert(len%8 == 0);

    pl = (uint64_t *)region;
    ptop = pl + len/8;

    while(pl < ptop){
        tmp = ((*pl)<<1UL) & pw32c64.mask1;
        tmp2 = (*pl) & pw32c64.mask2;
        tmp2 = ((tmp2 << 1UL) - (tmp2 >> 31UL));
        *pl = (tmp ^ (tmp2 & pw32c64.prim));
        pl++;
    }

    return 1;
}

int region_shift_mul_w4(gfele_t *pdes, gfele_t *psrc, gfele_t multipler, int len, int ifxor){
    gfele_t *pcom;
    gfele_t val = multipler;
    gfele_t mask = (gfele_t)(1<<3);

    if(val == 0){
        if(ifxor){
            return len;
        }else{
            memset(pdes, 0, len);
            return len;
        }
    }

    pcom = (gfele_t *)calloc(1, len);
    
    while((mask&val) == 0){
        mask = mask>>1;
    }
    while(mask > 1){
        if(mask&val){
            region_xor(pcom, psrc, len);
        }
        region_mul_2_64_w4(pcom, len);
        mask = mask>>1;
    }
    if(val&1){
        region_xor(pcom, psrc, len);
    }
    
    if(ifxor){
        region_xor(pdes, pcom, len);
    }else{
        memcpy(pdes, pcom, len); 
    }

    free(pcom);
    return len;
}

int region_shift_mul_w8(gfele_t *pdes, gfele_t *psrc, gfele_t multipler, int len, int ifxor){
    gfele_t *pcom;
    gfele_t val = multipler;
    gfele_t mask = (gfele_t)(1<<7);

    if(val == 0){
        if(ifxor){
            return len;
        }else{
            memset(pdes, 0, len);
            return len;
        }
    }

    pcom = (gfele_t *)calloc(1, len);
    
    while((mask&val) == 0){
        mask = mask>>1;
    }
    while(mask > 1){
        if(mask&val){
            region_xor(pcom, psrc, len);
        }
        region_mul_2_64_w8(pcom, len);
        mask = mask>>1;
    }
    if(val&1){
        region_xor(pcom, psrc, len);
    }
    
    if(ifxor){
        region_xor(pdes, pcom, len);
    }else{
        memcpy(pdes, pcom, len); 
    }

    free(pcom);
    return len;
}


int region_shift_mul_w16(gfele_t *pdes, gfele_t *psrc, gfele_t multipler, int len, int ifxor){
    gfele_t *pcom;
    gfele_t val = multipler;
    gfele_t mask = (gfele_t)(1<<15UL);

    if(val == 0){
        if(ifxor){
            return len;
        }else{
            memset(pdes, 0, len);
            return len;
        }
    }

    pcom = (gfele_t *)calloc(1, len);

    while((mask&val) == 0){
        mask = mask>>1;
    }
    while(mask > 1){
        if(mask&val){
            region_xor(pcom, psrc, len);
        }
        region_mul_2_64_w16(pcom, len);
        mask = mask>>1;
    }
    if(val&1){
        region_xor(pcom, psrc, len);
    }
    
    if(ifxor){
        region_xor(pdes, pcom, len);
    }else{
        memcpy(pdes, pcom, len); 
    }

    free(pcom);
    return len;
}


int region_shift_mul_w32(gfele_t *pdes, gfele_t *psrc, gfele_t multipler, int len, int ifxor){
    gfele_t *pcom;
    gfele_t val = multipler;
    gfele_t mask = (gfele_t)(1<<31UL);

    if(val == 0){
        if(ifxor){
            return len;
        }else{
            memset(pdes, 0, len);
            return len;
        }
    }

    pcom = (gfele_t *)calloc(1, len);

    while((mask&val) == 0){
        mask = mask>>1;
    }
    while(mask > 1){
        if(mask&val){
            region_xor(pcom, psrc, len);
        }
        region_mul_2_64_w32(pcom, len);
        mask = mask>>1;
    }
    if(val&1){
        region_xor(pcom, psrc, len);
    }
    
    if(ifxor){
        region_xor(pdes, pcom, len);
    }else{
        memcpy(pdes, pcom, len); 
    }

    free(pcom);
    return len;
}


int region_mul_2_w16_sse(gfele_t *des, gfele_t *src, int len, int ifxor){
    int i;

    __m128i *mpsrc = (__m128i *)src;
    __m128i *mpdes = (__m128i *)des;
    __m128i mprim = _mm_set_epi16(
            prim.w16, prim.w16, prim.w16, prim.w16, 
            prim.w16, prim.w16, prim.w16, prim.w16);
    __m128i hmask = _mm_set_epi16(
        (1<<15UL), (1<<15UL), (1<<15UL), (1<<15UL),
        (1<<15UL), (1<<15UL), (1<<15UL), (1<<15UL));
    __m128i lmask;
    __m128i hbit;
    __m128i mtemp;

    if(ifxor == 0){
        for(i =0; i < len/16; ++i){
            hbit = _mm_and_si128(mpsrc[i], hmask);
            lmask = _mm_sub_epi16(_mm_slli_epi16(hbit, 1) , _mm_srli_epi16(hbit, 15));
            mtemp = _mm_slli_epi16(mpsrc[i], 1);
            mpdes[i] = _mm_xor_si128(mtemp, _mm_and_si128(lmask, mprim));
        }
    }else{
        for(i =0; i < len/16; ++i){
            hbit = _mm_and_si128(mpsrc[i], hmask);
            lmask = _mm_sub_epi16(_mm_slli_epi16(hbit, 1) , _mm_srli_epi16(hbit, 15));
            mtemp = _mm_slli_epi16(mpsrc[i], 1);
            mtemp = _mm_xor_si128(mtemp, _mm_and_si128(lmask, mprim));
            mpdes[i] = _mm_xor_si128(mpsrc[i], mpdes[i]);
        }
    }

    return 1;
}

int region_mul_2_w32_sse(gfele_t *des, gfele_t *src, int len, int ifxor){
    int i;
    __m128i *mpsrc = (__m128i *)src;
    __m128i *mpdes = (__m128i *)des;
    __m128i mprim = _mm_set_epi32(prim.w32, prim.w32, prim.w32, prim.w32);
    __m128i hmask = _mm_set_epi32((1<<31UL), (1<<31UL), (1<<31UL), (1<<31UL));
    __m128i lmask;
    __m128i hbit;
    __m128i mtemp;

    if(ifxor == 0){
        for(i =0; i < len/16; ++i){
            hbit = _mm_and_si128(mpsrc[i], hmask);
            lmask = _mm_sub_epi32(_mm_slli_epi32(hbit, 1) , _mm_srli_epi32(hbit, 31));
            mtemp = _mm_slli_epi32(mpsrc[i], 1);
            mpdes[i] = _mm_xor_si128(mtemp, _mm_and_si128(lmask, mprim));
        }
    }else{
        for(i =0; i < len/16; ++i){
            hbit = _mm_and_si128(mpsrc[i], hmask);
            lmask = _mm_sub_epi32(_mm_slli_epi32(hbit, 1) , _mm_srli_epi32(hbit, 31));
            mtemp = _mm_slli_epi32(mpsrc[i], 1);
            mtemp = _mm_xor_si128(mtemp, _mm_and_si128(lmask, mprim));
            mpdes[i] = _mm_xor_si128(mtemp, mpdes[i]);
        }
    }
    return 1;
}

int gfs_init(gfs_t *gfs, int w){
    
    gfs->mul = NULL;
    gfs->div = NULL;
    gfs->inv = NULL;

    switch(w){
        case 4:     
            gfs->region_mul = region_shift_mul_w4;
            gfs->region_mul2 = region_mul_2_64_w4;
            break;
        case 8: 
            gfs->region_mul = region_shift_mul_w8;
            gfs->region_mul2 = region_mul_2_64_w8;
            break;
        case 16:
            gfs->region_mul = region_shift_mul_w16;
            gfs->region_mul2 = region_mul_2_64_w16;
            break;
        case 32:
            gfs->region_mul = region_shift_mul_w32;
            gfs->region_mul2 = region_mul_2_64_w32;
            break;
        default:
            printf("ERROR : bad w!\n");
            return 0;
    }

    return 1;
}
