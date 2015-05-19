#include "zcode.h"
#include "zcode_struct.h"
#include "code_common.h"
#include "file_operations.h"
#include "mcoding.h"

int z_encode(z_info_t *pzinfo,                  /* input */
        const char *orig_data, int data_size,   /* input */
        char **encoded_data,                    /* output */
        char **encoded_parity, int *chunk_size) /* output */
{
    int col = pzinfo->pzlil->rawcol;
    int row = pzinfo->pzlil->row;
    int blocksize = get_block_size_by_col(data_size,pzinfo->pzlil->rawcol);
    unsigned char *pdes, *psrc;
        
    psrc = (unsigned char *)calloc(col, blocksize);
    pdes = (unsigned char *)calloc(row, blocksize);

    // set psrc 
    memcpy(psrc, orig_data, data_size);

    // encode 
    mxcoding_lil_ppg(pdes, psrc, blocksize, pzinfo->packetsize, pzinfo->pzlil, pzinfo->m, pzinfo->k);

    // store to output
    *encoded_data = (char*)psrc;
    *encoded_parity = (char*)pdes;
    *chunk_size = blocksize;

    return 0;
}

static void set_lil_rows(int *rows, int **dplist,
                         int num_data, int num_parity, int col)
{
    int i;
    for(i = 0; i < num_data; ++i){
        rows[i] = dplist[0][i];
    }
    for(i = 0; i < num_parity; ++i){
        rows[num_data+i] = dplist[1][i] + col;
    }
}

static void set_repair_lil(lil_t *repair_lil, z_info_t *pzinfo, int **dplist, int total, int num_data, int num_parity)
{
    int i;
    int col = pzinfo->pzlil->col;
    repair_lil->row = total;
    repair_lil->rawcol = pzinfo->pzlil->rawcol;
    repair_lil->col = col;
    repair_lil->data = (gfele_t *)zalloc(total*(col)*sizeof(gfele_t));
    for (i = 0; i < num_data; i++) {
        repair_lil->data[i*col+0] = dplist[0][i];
    }
    for (i = 0; i < num_parity; i++) {
        memcpy(&repair_lil->data[(num_data+i)*col], &pzinfo->pzlil->data[dplist[1][i]*col], col*sizeof(gfele_t));
    }
}

static void show_list(int *list, int num)
{
    int i;
    puts("list: ");
    for (i = 0; i < num; i++) {
        printf("%4d ", list[i]);
    }
    puts("");
}

static void del_allzero_cols_lil(lil_t *pzlil)
{
    int rawcol = pzlil->rawcol;
    int flag[rawcol+1];
    memset(flag, 0, sizeof(int)*rawcol);
    int i,j;
    for (i = 0; i < pzlil->row; i++) {
        flag[pzlil->data[i*pzlil->col + 0]] = 1;
        for (j = 1; j < pzlil->col; j++) {
            if (pzlil->data[i*pzlil->col+j] == 0) {
                break;
            }
            flag[pzlil->data[i*pzlil->col+j]] = 1;
        }
    }
    //show_list(flag, rawcol);
    int pre = flag[0], temp;
    flag[0] = 0;
    for (i = 1; i <= rawcol; i++) {
        temp = flag[i];
        flag[i] = flag[i-1]+pre;
        pre = temp;
    }
    //show_list(flag, rawcol);
    gfele_t *p;
    for (i = 0; i < pzlil->row; i++) {
        for (j = 0; j < pzlil->col; j++) {
            p = &pzlil->data[i*(pzlil->col)+j];
            *p = flag[*p];
        }
    }
    pzlil->rawcol = flag[rawcol];
}


// get @num row of @from, start of @start to @to
static void get_part_lil(lil_t *to, lil_t *from,int row_start, int row_num)
{
    to->col = from->col;
    to->rawcol = from->rawcol;
    to->row = row_num;
    to->data = (gfele_t*)zalloc(row_num*(to->col)*sizeof(gfele_t));
    memcpy(to->data, &(from->data[row_start*(from->col)]), row_num*(to->col)*sizeof(gfele_t));
}

int z_repair_chunk_needed(int m, int k, int node, /* input */
        int chunk_num, /* input */
        int *chunk_list)         /* output */
{
    int num_per_node;
    int r = ZMAT_R(m, k);
    int num_data;
    int num_parity;
    int total;
    int **dplist;

    if (chunk_num != (r*(k+m-1)/m)) {
        fprintf(stderr, "chunk num error\n");
        return 1;
    }

    num_per_node = r/m;
    num_data = (k-1)*num_per_node;
    num_parity = m*num_per_node;
    total = num_data + num_parity;

    dplist = get_repair_list(m, k, node);

    // set rows
    int rows[total];
    set_lil_rows(rows, dplist, num_data, num_parity, k*r);
    int i;
    for (i = 0; i < total; i++) {
        chunk_list[i] = rows[i];
    }

    free(dplist[0]);
    dplist[0] = NULL;
    free(dplist[1]);
    dplist[1] = NULL;
    free(dplist);
    dplist = NULL;

    return 0;
}

int z_repair(z_info_t *pzinfo,
        char *available_data,                        /* input */
        int *data_list, int data_num, int chunk_len, /* input */
        int node,                                   /* input */
        char **out_data)                            /* output */
{
    if (node < 0 || node >= pzinfo->k) {
        print_error("ERROR: node num:%d invalid\n", node);
        return 0;
    }

    int fragment; // numbers of repair block in one node
    int num_per_node;
    int r = ZMAT_R(pzinfo->m, pzinfo->k);
    int num_data;
    int num_parity;
    int total;
    int **dplist;

    fragment = (pzinfo->pzlil->rawcol)/(pzinfo->k); 
    num_per_node = r/pzinfo->m;
    num_data = (pzinfo->k-1)*num_per_node;
    num_parity = pzinfo->m*num_per_node;
    total = num_data + num_parity;
    if (total != data_num) {
        fprintf(stderr, "data num error\n");
        return 1;
    }

    dplist = get_repair_list(pzinfo->m, pzinfo->k, node);
    // print_repair_list(dplist, pzinfo->m, pzinfo->k);

    // set rows
    int rows[total];
    set_lil_rows(rows, dplist, num_data, num_parity,pzinfo->pzlil->rawcol);
    int i;
    for (i = 0; i < total; i++) {
        if (rows[i] != data_list[i]) {
            fprintf(stderr, "data list error\n");
            return 1;
        }
    }

    int block_size;
    block_size = chunk_len;
    // set repair source data
    unsigned char *psrc, *pdes;
    psrc = (unsigned char*)available_data;
    pdes = (unsigned char *)zalloc((fragment)*(block_size));

    lil_t repair_lil;
    set_repair_lil(&repair_lil, pzinfo, dplist, total, num_data, num_parity);
    free(dplist[0]);
    dplist[0] = NULL;
    free(dplist[1]);
    dplist[1] = NULL;
    free(dplist);
    dplist = NULL;

    // remove empty col
    del_allzero_cols_lil(&repair_lil);
    if (repair_lil.rawcol != repair_lil.row) {
        print_error("rawcol:%d != row:%d, error\n", repair_lil.rawcol, repair_lil.row);
        return 1;
    }

    // inverse repair_lil
    gfm_t gf;
    gf_init(&gf, 8);
    inverse_lil(&repair_lil, &gf);
    gf_free(&gf);

    // get fragment numbers of repair_lil cols
    lil_t part_repair_lil;
    get_part_lil(&part_repair_lil, &repair_lil,node*num_per_node, fragment);
    zlil_free(&repair_lil);

    // mxcoding_lil_ppg to repair data
    mxcoding_lil_ppg(pdes, psrc, block_size, pzinfo->packetsize, &part_repair_lil, pzinfo->m, pzinfo->k);
    zlil_free(&part_repair_lil);

    *out_data = (char*)pdes;

    return 0;
}

int z_init(z_coder_t *pz, int m, int k, int packetsize)
{
    // set coding info
    pz->pzi = (z_info_t *)zalloc(sizeof(z_info_t));

    pz->pzi->pzlil = (lil_t *)zalloc(sizeof(lil_t));
    if (make_z_lil(pz->pzi->pzlil, m, k) == 0) {
        print_error("make_z_lil error\n");
        return 0;
    }
    
    pz->pzi->m = m;
    pz->pzi->k = k;

    pz->pzi->packetsize = packetsize;
    // pz->pzi->blocksize = get_block_size_by_col(pz->pzi->filesize,pz->pzi->pzlil->rawcol);

    // set coding methods
    pz->pzm = NULL;
    // TODO: remove pzm
    // pz->pzm = (zm_t *)zalloc(sizeof(zm_t));
    // pz->pzm->encode = z_encode;
    // pz->pzm->decode = z_decode;
    // pz->pzm->repair = z_repair;

    return 1;
}

int z_free(z_coder_t *pz)
{
    // free coding info
    zlil_free(pz->pzi->pzlil);
    free(pz->pzi->pzlil);

    free(pz->pzi);
    pz->pzi = NULL;

    // free coding methods
    free(pz->pzm);
    pz->pzm = NULL;

    return 1;
}
