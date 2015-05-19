#include "file_operations.h"
#include "mdsz.h"
#include "mcoding.h"
#include "zcode_struct.h"

int mdsz_encode(mdsz_info_t *pmdszi)
{
    int col = pmdszi->pcoomat->lil_pos.rawcol;
    int row = pmdszi->pcoomat->lil_pos.row;
    int blocksize = pmdszi->blocksize;
    unsigned char *pdes, *psrc;
        
    psrc = (unsigned char *)calloc(col, blocksize);
    pdes = (unsigned char *)calloc(row, blocksize);

    // set psrc 
    if (!read_single_file(pmdszi->src_filename, pmdszi->filesize, psrc)) {
        fprintf(stderr, "read file error!\n");
        free(pdes);
        free(psrc);
        return 0;
    }

    // encode 
    gf_t gf;
    gf_init_easy(&gf, 8);
    mcoding_coomat_ppg(pdes, psrc, pmdszi->blocksize, pmdszi->packetsize, pmdszi->pcoomat, pmdszi->m, pmdszi->k, &gf);
    gfc_free(&gf, 0);

    // store to file
    char *des_filename = pmdszi->des_filename;
    if(!bat_write_bynums(des_filename, col, psrc, blocksize)) {
        fprintf(stderr, "bat write by numbs error\n");
        free(pdes);
        free(psrc);
        return 0;
    }

    int list[row];
    int i;
    for (i=0; i<row; i++) {
        list[i] = i+col;
    }

    if (!bat_write_bylist(des_filename, list, row, pdes, blocksize)) {
        fprintf(stderr, "bat write by list error\n");
        free(pdes);
        free(psrc);
        return 0;
    }

    free(psrc);
    free(pdes);
    return 1;
}

int mdsz_decode(mdsz_info_t *pmdszi)
{
    int col = pmdszi->pcoomat->lil_pos.rawcol;

    int *list = (int *)zalloc(sizeof(int)*(col));
    int i;
    for (i=0; i<col; i++) {
        list[i] = i;
    }

    char *src_filename = pmdszi->des_filename;
    unsigned char *psrc;
    psrc = (unsigned char *)zalloc(col*(pmdszi->blocksize));
    if (!bat_read(src_filename, list, col, psrc, pmdszi->blocksize)) {
        fprintf(stderr, "bat_read error\n");
        free(list);
        free(psrc);
        return 0;
    }
    free(list);

    if (!write_2single_file(src_filename, pmdszi->filesize, psrc)) {
        fprintf(stderr, "write file error!\n");
        free(psrc);
        return 0;
    }
    return 1;
}

static void set_coomat_rows(int *rows, int **dplist,
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

static int init_src_data(unsigned char *psrc, mdsz_info_t *pmdszi, int *rows, int total)
{
    char *src_filename = pmdszi->des_filename;
    if(!bat_read(src_filename, rows, total, psrc, pmdszi->blocksize)) {
        print_error("bat read error\n");
        return 0;
    }
    return 1;
}

static void set_repair_coomat(coomat_t *repair_coomat, mdsz_info_t *pmdszi, int **dplist, int total, int num_data, int num_parity)
{
    int i;
    int col = pmdszi->pcoomat->lil_pos.col;
    repair_coomat->lil_pos.row = total;
    repair_coomat->lil_pos.rawcol = pmdszi->pcoomat->lil_pos.rawcol;
    repair_coomat->lil_pos.col = col;
    repair_coomat->lil_pos.data = (gfele_t *)zalloc(total*(col)*sizeof(gfele_t));
    mat_init(&repair_coomat->mat_val);
    make_zero(&repair_coomat->mat_val, total, col);
    for (i = 0; i < num_data; i++) {
        repair_coomat->lil_pos.data[i*col+0] = dplist[0][i];
        repair_coomat->mat_val.data[i*col+0] = 1;
    }
    for (i = 0; i < num_parity; i++) {
        memcpy(&repair_coomat->lil_pos.data[(num_data+i)*col], &pmdszi->pcoomat->lil_pos.data[dplist[1][i]*col], col*sizeof(gfele_t));
        memcpy(&repair_coomat->mat_val.data[(num_data+i)*col], &pmdszi->pcoomat->mat_val.data[dplist[1][i]*col], col*sizeof(gfele_t));
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
static void get_part_coomat(coomat_t *to, coomat_t *from,int row_start, int row_num)
{
    to->lil_pos.col = from->lil_pos.col;
    to->lil_pos.rawcol = from->lil_pos.rawcol;
    to->lil_pos.row = row_num;
    to->lil_pos.data = (gfele_t*)zalloc(row_num*(to->lil_pos.col)*sizeof(gfele_t));
    mat_init(&to->mat_val);
    make_zero(&to->mat_val, row_num, from->lil_pos.col);
    memcpy(to->lil_pos.data, &(from->lil_pos.data[row_start*(from->lil_pos.col)]), row_num*(to->lil_pos.col)*sizeof(gfele_t));
    memcpy(to->mat_val.data, &(from->mat_val.data[row_start*(from->lil_pos.col)]), row_num*(to->lil_pos.col)*sizeof(gfele_t));
}

int mdsz_repair(mdsz_info_t *pmdszi, int node)
{
    if (node < 0 || node >= pmdszi->k) {
        print_error("ERROR: node num:%d invalid\n", node);
        return 0;
    }

    int fragment; // numbers of repair block in one node
    int num_per_node;
    int r = ZMAT_R(pmdszi->m, pmdszi->k);
    int num_data;
    int num_parity;
    int total;
    int **dplist;
    gfm_t *pgf=&pmdszi->gf;

    fragment = (pmdszi->pcoomat->lil_pos.rawcol)/(pmdszi->k); 
    num_per_node = r/pmdszi->m;
    num_data = (pmdszi->k-1)*num_per_node;
    num_parity = pmdszi->m*num_per_node;
    total = num_data + num_parity;

    dplist = get_repair_list(pmdszi->m, pmdszi->k, node);
    //print_repair_list(dplist, pmdszi->m, pmdszi->k);

    // set rows
    int rows[total];
    set_coomat_rows(rows, dplist, num_data, num_parity,pmdszi->pcoomat->lil_pos.rawcol);
    //show_list(rows, total);

    // set repair source data
    unsigned char *psrc, *pdes;
    psrc = (unsigned char *)zalloc((total)*(pmdszi->blocksize));
    pdes = (unsigned char *)zalloc((fragment)*(pmdszi->blocksize));
    if (init_src_data(psrc, pmdszi, rows, total) == 0) {
        show_list(rows, total);
        free(psrc);
        free(pdes);
        return 0;
    }

    coomat_t repair_coomat;
    set_repair_coomat(&repair_coomat, pmdszi, dplist, total, num_data, num_parity);

    // remove empty col
    del_allzero_cols_lil(&repair_coomat.lil_pos);
    if (repair_coomat.lil_pos.rawcol != repair_coomat.lil_pos.row) {
        print_error("rawcol:%d != row:%d, error\n", repair_coomat.lil_pos.rawcol, repair_coomat.lil_pos.row);
        return 0;
    }

    // inverse repair_coomat
    inverse_coomat(&repair_coomat, pgf);
    //print_coomat(&repair_coomat);

    // get fragment numbers of repair_coomat cols
    coomat_t part_repair_coomat;
    get_part_coomat(&part_repair_coomat, &repair_coomat,node*num_per_node, fragment);
    zcoomat_free(&repair_coomat);

    // mxcoding_lil_ppg to repair data
    gf_t gfc;
    gf_init_easy(&gfc, 8);
    mcoding_coomat_ppg(pdes, psrc, pmdszi->blocksize, pmdszi->packetsize, &part_repair_coomat, pmdszi->m, pmdszi->k, &gfc);
    zcoomat_free(&part_repair_coomat);
    gfc_free(&gfc, 0);
    // store files
    int start = node * fragment, end = (node+1)*fragment-1;
    // store to file
    int repair_list[fragment];
    int i;
    for (i = start; i <= end; i++) {
        repair_list[i-start] = i;
    }

    char *des_filename = pmdszi->des_filename;
    if (!bat_write_bylist(des_filename,repair_list, fragment, pdes, pmdszi->blocksize)) {
        print_error("bat write bylist error\n");
        free(pdes);
        free(psrc);
        return 0;
    }

    free(pdes);
    free(psrc);
    return 1;
}

int mdsz_init(mdsz_coder_t *pmdsz, int m, int k, const char *des_filepath, const char *src_filename, int packetsize)
{
    // set coding info
    pmdsz->pmdszi = (mdsz_info_t *)zalloc(sizeof(mdsz_info_t));

    pmdsz->pmdszi->pcoomat= (coomat_t*)zalloc(sizeof(coomat_t));
    gfmat_t mat_van;
    mat_init(&mat_van);

    gfm_t *pgf = &pmdsz->pmdszi->gf;
    gf_init(pgf, 8);

    make_parity_vandermonde(&mat_van, m, k, pgf);
    make_z_coomat(pmdsz->pmdszi->pcoomat, &mat_van, m, k);
    mat_free(&mat_van);

    pmdsz->pmdszi->m = m;
    pmdsz->pmdszi->k = k;

    int path_len, name_len;
    path_len  = strlen(des_filepath);
    name_len = strlen(src_filename);
    pmdsz->pmdszi->des_filename = (char *)zalloc(path_len+name_len+1);
    get_des_filename(pmdsz->pmdszi->des_filename, des_filepath, src_filename);
    pmdsz->pmdszi->src_filename = (char *)zalloc(name_len+1);
    strcpy(pmdsz->pmdszi->src_filename, src_filename);

    pmdsz->pmdszi->filesize = get_filesize(src_filename);

    pmdsz->pmdszi->packetsize = packetsize;
    pmdsz->pmdszi->blocksize = get_block_size_by_col(pmdsz->pmdszi->filesize,pmdsz->pmdszi->pcoomat->lil_pos.rawcol);

    // set coding methods
    pmdsz->pmdszm = (mdszm_t *)zalloc(sizeof(mdszm_t));
    pmdsz->pmdszm->encode = mdsz_encode;
    pmdsz->pmdszm->decode = mdsz_decode;
    pmdsz->pmdszm->repair = mdsz_repair;
    return  1;
}

int mdsz_free(mdsz_coder_t *pmdsz)
{
    // free coding info
    zcoomat_free(pmdsz->pmdszi->pcoomat);
    gf_free();
    free(pmdsz->pmdszi->pcoomat);

    free(pmdsz->pmdszi->des_filename);
    free(pmdsz->pmdszi->src_filename);
    free(pmdsz->pmdszi);
    pmdsz->pmdszi = NULL;

    // free coding methods
    free(pmdsz->pmdszm);
    pmdsz->pmdszm = NULL;

    return 1;
}
