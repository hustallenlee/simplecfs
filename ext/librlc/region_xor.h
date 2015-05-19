#pragma once
#include "galois.h"

#define FALSE 8000
#define TRUE  8001
#define AVX_SUPPORT FALSE
#define SSE_SUPPORT FALSE

/*
 * region_xor
 */
int region_xor(void *dst, void*src, int len);
int region_xor_8(void * dst, void* src, int len);
int region_xor_64(void* dst, void* src, int len);
int region_xor_sse(void* dst, void* src, int len);
