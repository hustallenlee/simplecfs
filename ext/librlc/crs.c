#include "crs.h"
#include "file_operations.h"
#include "mcoding.h"

/** encode and store to separate files
 * @param pcrsi, crs information,
 *
 * return 1 in case of error, otherwise return 0;
 */
int crs_encode(crs_info_t *pcrsi,                  /* input */
        const char *orig_data, int data_size,   /* input */
        char **encoded_data,                    /* output */
        char **encoded_parity, int *chunk_size) /* output */
{
    int n = pcrsi->n, k = pcrsi->k;
    int packet_size = pcrsi->packet_size;
    int file_size = data_size;
    gfmat_t parity_mat;


    int block_size;
    block_size = get_block_size(file_size, pcrsi->pmat);

    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)zalloc(k*block_size);
    assert(psrc != NULL);
    pdes = (unsigned char *)zalloc((n-k)*block_size);
    assert(pdes != NULL);
    memcpy(psrc, orig_data, data_size);

    mat_init(&parity_mat);
    get_part_of_matrix(&parity_mat, pcrsi->pmat, k, n-k);
    mxcoding_pbg(pdes, psrc, block_size, packet_size, &parity_mat);
    
    // store to output
    *encoded_data = (char*)psrc;
    *encoded_parity =(char*)pdes;
    *chunk_size = block_size;
    mat_free(&parity_mat);
    return 0;
}

/** decode and get the original file
 * @param pcrsi, crs information,
 * @param phelp, row num of data to help decode, len of k(data devices size).
 *
 * return 1 in case of error, otherwise return 0;
 */
int crs_decode(crs_info_t *pcrsi,
        char *available_data,                           /* input */
        int *data_list, int data_num, int chunk_len,    /* input */
        char **out_data)                               /* output */
{
    int k = pcrsi->k;
    int packet_size = pcrsi->packet_size;
    gfmat_t decode_mat;

    if (data_num < k) {
        fprintf(stderr, "crs_decode phelp len < k\n");
        return 1;
    }
    mat_init(&decode_mat);
    select_by_rows(&decode_mat, data_list, k, pcrsi->pmat);
    inverse_matrix(&decode_mat, pcrsi->pgf);

    int block_size;
    block_size = chunk_len;
    
    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)available_data;
    pdes = (unsigned char *)malloc(k*block_size);
    assert(pdes != NULL);

    mxcoding_pbg(pdes, psrc, block_size, packet_size, &decode_mat);

    *out_data = (char *)pdes;
    mat_free(&decode_mat);
    return 0;
}

int crs_repair(crs_info_t *pcrsi,
        char *available_data,                        /* input */
        int *data_list, int data_num, int chunk_len, /* input */
        int *repair_list, int repair_num,            /* input */
        char **out_data)                            /* output */
{
    int k = pcrsi->k;
    int packet_size = pcrsi->packet_size;
    gfmat_t repair_mat, gen_mat, inter_mat;

    if (data_num < k) {
        fprintf(stderr, "crs_repair phelp len < k\n");
        return 1;
    }
    mat_init(&repair_mat);
    select_by_rows(&repair_mat, data_list, k, pcrsi->pmat);
    inverse_matrix(&repair_mat, pcrsi->pgf);
    mat_init(&gen_mat);
    select_by_rows(&gen_mat, repair_list, repair_num, pcrsi->pmat);
    mat_init(&inter_mat);
    prod(&inter_mat, &gen_mat, &repair_mat, pcrsi->pgf);

    int block_size;
    block_size = chunk_len;
    
    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)available_data;
    pdes = (unsigned char *)malloc(repair_num*block_size);
    assert(pdes != NULL);

    mxcoding_pbg(pdes, psrc, block_size, packet_size, &inter_mat);

    *out_data = (char *)pdes;
    mat_free(&inter_mat);
    mat_free(&gen_mat);
    mat_free(&repair_mat);
    return 0;
}

int crs_init(crs_coder_t *crs, int n, int k, int word, int packet_size)
{
    assert(crs);

    // set coding information
    crs->pcrsi = (crs_info_t *)malloc(sizeof(crs_info_t));
    assert(crs->pcrsi);
    crs->pcrsi->pgf = (gfm_t *)malloc(sizeof(gfm_t));
    assert(crs->pcrsi->pgf);
    gf_init(crs->pcrsi->pgf, word);

    gfmat_t temp_mat;
    mat_init(&temp_mat);

    crs->pcrsi->pmat = (gfmat_t *)malloc(sizeof(gfmat_t));
    assert(crs->pcrsi->pmat);
    mat_init(crs->pcrsi->pmat);

    make_sys_cauchy(&temp_mat, n, k, crs->pcrsi->pgf);
    transform_to_bitmatrix(crs->pcrsi->pmat, &temp_mat, crs->pcrsi->pgf, word);
    mat_free(&temp_mat);

    crs->pcrsi->n = n*word;
    crs->pcrsi->k = k*word;

    crs->pcrsi->packet_size = packet_size;
    
    // set coding methods
    crs->pcrsm = NULL;
    // TODO: remove pcrsm
    // crs->pcrsm = (crsm_t *)malloc(sizeof(crsm_t));
    // assert(crs->pcrsm);
    // crs->pcrsm->encode = crs_encode;
    // crs->pcrsm->decode = crs_decode;
    // crs->pcrsm->repair = crs_repair;

    return 1;
}


int crs_free(crs_coder_t *crs)
{
    // free coding information
    // free matrix
    mat_free(crs->pcrsi->pmat);
    free(crs->pcrsi->pmat);

    // free gf
    gf_free(crs->pcrsi->pgf);
    free(crs->pcrsi->pgf);
    free(crs->pcrsi);
    crs->pcrsi = NULL;

    // free coding methods.
    free(crs->pcrsm);
    crs->pcrsm = NULL;

    return 1;
}
