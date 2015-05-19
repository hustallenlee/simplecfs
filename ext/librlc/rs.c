#include "rs.h"
#include "file_operations.h"
#include "mcoding.h"

/** encode and store to separate files
 * @param prsi, rs information,
 * @param orig_data, data to be encoded
 * @param data_len, orig data len
 * @param encoded_data, data after encoded, store in an array of k*chunk_size
 * @param encoded_parity, parity data , store in and array of m*chunk_size
 * @param chunk_size, store the chunk size, data and parity are k+m chunk
 *
 * return 0 in case of success , otherwise return 1;
 * caller should free the encoded_data, encoded_parity
 */
int rs_encode(rs_info_t *prsi,                  /* input */
        const char *orig_data, int data_size,   /* input */
        char **encoded_data,                    /* output */
        char **encoded_parity, int *chunk_size) /* output */
{
    int n = prsi->n, k = prsi->k;
    int packet_size = prsi->packet_size;
    int file_size = data_size;
    gfmat_t parity_mat;


    int block_size;
    block_size = get_block_size(file_size, prsi->pmat);

    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)zalloc(k*block_size);
    assert(psrc != NULL);
    pdes = (unsigned char *)zalloc((n-k)*block_size);
    assert(pdes != NULL);
    memcpy(psrc, orig_data, data_size);

    mat_init(&parity_mat);
    get_part_of_matrix(&parity_mat, prsi->pmat, k, n-k);
    mcoding_pbg(pdes, psrc, block_size, packet_size, &parity_mat, prsi->pgf);
    
    // store to output
    *encoded_data = (char*)psrc;
    *encoded_parity =(char*)pdes;
    *chunk_size = block_size;
    mat_free(&parity_mat);
    return 0;
}

/**
 * Reconstruct original data from a set of k encoded chunk
 *
 * @param prsi- rs information
 * @param available_data - erasure encoded chunk (k*chunk_len)
 * @param data_list - number of fragments being passed in(>=k)
 * @param data_num - num of data chunk(>=k)
 * @param chunk_len - length of each chunk(assume they are the same)
 * @param out_data - _output_ pointer to decoded data
 *          (output data pointers are allocated by librlc,
 *           caller invokes librlc_decode_clean() after it has
 *           read decoded data in 'out_data')
 *
 * @return 0 on success, -error code otherwise
 */
int rs_decode(rs_info_t *prsi,
        char *available_data,                           /* input */
        int *data_list, int data_num, int chunk_len,   /* input */
        char **out_data)                                /* output */
{
    int k = prsi->k;
    int packet_size = prsi->packet_size;
    gfmat_t decode_mat;

    if (data_num < k) {
        fprintf(stderr, "rs_decode chunk num < k\n");
        return 1;
    }
    mat_init(&decode_mat);
    select_by_rows(&decode_mat, data_list, k, prsi->pmat);
    inverse_matrix(&decode_mat, prsi->pgf);

    int block_size;
    block_size = chunk_len;
    
    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)available_data;
    pdes = (unsigned char *)malloc(k*block_size);
    assert(pdes != NULL);

    mcoding_pbg(pdes, psrc, block_size, packet_size, &decode_mat, prsi->pgf);

    *out_data = (char *)pdes;
    mat_free(&decode_mat);
    return 0;
}

/**
 * Reconstruct  missing fragments from a subset of available fragments
 *
 * @param prsi - rs information
 * @param available_data- erasure encoded chunks 
 * @param data_num - number of chunks being passed in
 * @param chunk_len - size in bytes of the chunk
 * @param repair_list - missing chunks' index to reconstruct
 * @param repair_num - missing chunks' num to reconstruct
 * @param out_data - output of reconstruct
 *
 * @return 0 on success, -error code otherwise
 */
int rs_repair(rs_info_t *prsi,
        char *available_data,                        /* input */
        int *data_list, int data_num, int chunk_len, /* input */
        int *repair_list, int repair_num,            /* input */
        char **out_data)                            /* output */
//int rs_repair(rs_info_t *prsi, blist_t *phelp, blist_t *pgen)
{
    int k = prsi->k;
    int packet_size = prsi->packet_size;
    gfmat_t repair_mat, gen_mat, inter_mat;

    if (data_num < k) {
        fprintf(stderr, "rs_repair phelp len < k\n");
        return 1;
    }
    mat_init(&repair_mat);
    select_by_rows(&repair_mat, data_list, k, prsi->pmat);
    inverse_matrix(&repair_mat, prsi->pgf);
    mat_init(&gen_mat);
    select_by_rows(&gen_mat, repair_list, repair_num, prsi->pmat);
    mat_init(&inter_mat);
    prod(&inter_mat, &gen_mat, &repair_mat, prsi->pgf);

    int block_size;
    block_size = chunk_len;
    
    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)available_data;
    pdes = (unsigned char *)malloc(repair_num*block_size);
    assert(pdes != NULL);

    mcoding_pbg(pdes, psrc, block_size, packet_size, &inter_mat, prsi->pgf);

    *out_data = (char *)pdes;
    mat_free(&inter_mat);
    mat_free(&gen_mat);
    mat_free(&repair_mat);
    return 0;
}

int rs_init(rs_coder_t *rs, int n, int k, int word, int packet_size)
{
    // set coding information
    rs->prsi = (rs_info_t *)malloc(sizeof(rs_info_t));
    assert(rs->prsi);

    rs->prsi->pgf = (gfm_t *)malloc(sizeof(gfm_t));
    assert(rs->prsi->pgf);
    gf_init(rs->prsi->pgf, word);

    rs->prsi->pmat = (gfmat_t *)malloc(sizeof(gfmat_t));
    assert(rs->prsi->pmat);
    mat_init(rs->prsi->pmat);
    make_sys_vandermonde(rs->prsi->pmat, n, k, rs->prsi->pgf);

    rs->prsi->n = n;
    rs->prsi->k = k;

    rs->prsi->packet_size = packet_size;
    
    // set coding methods
    rs->prsm = NULL;
    // TODO:remove prsm
    // rs->prsm = (rsm_t *)malloc(sizeof(rsm_t));
    // assert(rs->prsm);
    // rs->prsm->encode = rs_encode;
    // rs->prsm->decode = rs_decode;
    // rs->prsm->repair = rs_repair;

    return 1;
}

int rs_free(rs_coder_t *rs)
{
    // free coding information
    gf_free(rs->prsi->pgf);
    free(rs->prsi->pgf);

    mat_free(rs->prsi->pmat);
    free(rs->prsi->pmat);

    free(rs->prsi);
    rs->prsi = NULL;

    // free coding methods
    free(rs->prsm);
    rs->prsm = NULL;

    return 1;
}

