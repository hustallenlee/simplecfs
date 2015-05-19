#include "zcode_struct.h"
#define NODEBUG 1

static mat_node *set_mat_node(gfele_t value, int pos)
{
    mat_node *pnode = (mat_node *)malloc(sizeof(mat_node));
    if (NULL == pnode) {
        printf("malloc failed\n");
        return NULL;
    }
    pnode->value = value;
    pnode->pos = pos;
    pnode->pnext = NULL;
    return pnode;
}

// add node to list end
// return 0 on success, other on fail
static int list_append(head_t *phead, mat_node *pnode)
{
    if (NULL == phead->phead) {
       phead->phead = pnode; 
       phead->len = 1;
       return 0;
    }
    mat_node *p = phead->phead;
    while (p->pnext != NULL) {
        p = p->pnext;
    }
    p->pnext = pnode;
    phead->len ++;
    return 0;
}

static void free_mat_list(head_t phead[], int len)
{
    int i;
    mat_node *p, *q;
    for (i = 0; i < len; i++) {
        p = phead[i].phead;
        while (p != NULL) {
            q = p->pnext;
            free(p);
            p = q;
        }
        phead[i].phead = NULL;
    }
}

static void swap_mat_head(head_t *a, head_t *b)
{
    head_t temp = *a;
    *a = *b;
    *b = temp;
}

static void mul_mat_head(head_t *phead, gfele_t value, gfm_t *gf)
{
    mat_node *p = phead->phead;
    while (p != NULL) {
        p->value = gf->mul(p->value, value);
        p = p->pnext;
    }
}

// to <= from * value
// return 0 on success
static int imul_mat_head(head_t *to, head_t *from, gfele_t prod, gfm_t *gf)
{
    mat_node *pfrom = from->phead;
    mat_node *pto = to->phead;
    mat_node *pto_pre = NULL;
    while (pfrom != NULL) {
        while((pto!=NULL) && (pto->pos < pfrom->pos)) {
            pto_pre = pto;
            pto = pto->pnext;
        }
        if ((NULL==pto) || (pto->pos > pfrom->pos)) {
            // add new node
            mat_node *temp = set_mat_node(0, pfrom->pos);
            if (NULL == temp) {
                return -1;
            }
            temp->value = gf->mul(pfrom->value, prod);

            if (NULL == pto_pre) {
                to->phead = temp;
                if (NULL == pto) {
                    pto = temp;
                } else {
                    pto_pre = temp;
                    temp->pnext = pto;
                }
            } else {
                pto_pre->pnext = temp;
                temp->pnext = pto;
                pto_pre = temp;
            }
            to->len ++;
        } else { // pto->pos == pfrom->pos
            pto->value ^= gf->mul(pfrom->value, prod);
            if (pto->value == 0) {
                // delete node
                if (NULL == pto_pre) {
                    to->phead = pto->pnext;
                    free(pto);
                    pto = to->phead;
                } else {
                    pto_pre->pnext = pto->pnext;
                    free(pto);
                    pto = pto_pre->pnext;
                }
                to->len --;
            }
        }
        pfrom = pfrom->pnext;
    }
    return 0;
}

static void show_mat_list(head_t mat_list[], int len)
{
    // for debug
#if NODEBUG
    (void)len;
    (void)mat_list;
#else
    int i;
    mat_node *p;
    for (i = 0; i < len; i++) {
        p =mat_list[i].phead;
        printf("%3d: ", i);
        printf("len: %d ", mat_list[i].len);
        while (p != NULL) {
            printf("pos:%d value:%x  ", p->pos, p->value);
            p = p->pnext;
        }
        puts("");
    }
    puts("");
#endif
}

static int inverse_implement(head_t *mat_list_raw, head_t *mat_list_indentity, int row, gfm_t *gf)
{
    int i, j, pos;

    for (i = 0; i < row; i++) {
        mat_node *p = set_mat_node(1, i);
        if (NULL == p) {
            free_mat_list(mat_list_raw, row);
            free_mat_list(mat_list_indentity, row);
            print_error("set node error\n");
            return -1;
        }
        list_append(&mat_list_indentity[i], p);
    }

    // start reverse
    for (i = 0; i < row; i++) {
        pos = i;
        if (NULL == mat_list_raw[pos].phead) {
            free_mat_list(mat_list_raw, row);
            free_mat_list(mat_list_indentity, row);
            print_error("empty row, cann't  inverse\n");
            return -1;
        }
        if (mat_list_raw[i].phead->pos != i) {
            do {
                ++ pos;
                if (NULL == mat_list_raw[pos].phead || pos >= row) {
                    free_mat_list(mat_list_raw, row);
                    free_mat_list(mat_list_indentity, row);
                    print_error("can find row\n");
                    return -1;
                }
            } while (mat_list_raw[pos].phead->pos != i);
            swap_mat_head(&mat_list_raw[i], &mat_list_raw[pos]);
            swap_mat_head(&mat_list_indentity[i], &mat_list_indentity[pos]);
        }

        gfele_t value;
        if (mat_list_raw[i].phead->value != 1) {
            value = gf->div(1, mat_list_raw[i].phead->value);
            mul_mat_head(&mat_list_raw[i], value, gf);
            mul_mat_head(&mat_list_indentity[i], value, gf);
        }

        mat_node *pcol; // the col to handle
        for (j = 0; j < i; j++) {
            pcol = mat_list_raw[j].phead->pnext;
            if (NULL == pcol) {
                continue;
            }
            if (pcol->pos != i) {
                continue;
            }
            value = pcol->value;
            imul_mat_head(&mat_list_raw[j], &mat_list_raw[i], value, gf);
            imul_mat_head(&mat_list_indentity[j], &mat_list_indentity[i], value, gf);
        }
        for (j = i+1; j < row; j++) {
            pcol = mat_list_raw[j].phead;
            if (NULL == pcol) {
                free_mat_list(mat_list_raw, row);
                free_mat_list(mat_list_indentity, row);
                print_error("empty row, cann't  inverse\n");
                return -1;
            }
            if (pcol->pos !=i) {
                continue;
            }
            value = pcol->value;
            imul_mat_head(&mat_list_raw[j], &mat_list_raw[i], value, gf);
            imul_mat_head(&mat_list_indentity[j], &mat_list_indentity[i], value, gf);
        }
    }

    return 0;
}
// inverse the coomat_t matrix
// return: 0 on success
int inverse_coomat(coomat_t *pcoomat, gfm_t *gf)
{
    int i, j;
    int row = pcoomat->lil_pos.row;
    int col = pcoomat->lil_pos.col;
    head_t *mat_list_raw = (head_t*)malloc(row*sizeof(head_t));
    head_t *mat_list_indentity=(head_t*)malloc(row*sizeof(head_t));
    gfmat_t *pmat_val = &(pcoomat->mat_val);
    lil_t *plil_pos = &(pcoomat->lil_pos);

    for (i = 0; i < row; i++) {
        mat_list_raw[i].len = 0;
        mat_list_raw[i].phead = NULL;
        mat_list_indentity[i].len = 0;
        mat_list_indentity[i].phead = NULL;
    }

    for (i = 0; i < row; i++) {
        for (j = 0; j < col; j++) {
            if (j!=0 && plil_pos->data[i*col+j] == 0) {
                break;
            }
            mat_node *p =  set_mat_node(pmat_val->data[i*col+j], plil_pos->data[i*col+j]);
            if (NULL == p) {
                free_mat_list(mat_list_raw, row);
                return -1;
            }
            list_append(&mat_list_raw[i], p);
        }
    }

    if (inverse_implement(mat_list_raw, mat_list_indentity, row, gf)) {
        print_error("inverse error\n");
        show_mat_list(mat_list_raw, row);
        show_mat_list(mat_list_indentity, row);
        return -1;
    }

    // after inverse
    //printf("after inverse coomat result:\n");
    //show_mat_list(mat_list_raw, row);
    //show_mat_list(mat_list_indentity, row);

    int newcol = col;
    for (i = 0; i < row; i++) {
        if (newcol < mat_list_indentity[i].len) {
            newcol = mat_list_indentity[i].len;
        }
    }
    //printf("newcol: %d\n", newcol);
    if (newcol == col) {
        memset(plil_pos->data, 0, col*row*sizeof(gfele_t));
        memset(pmat_val->data, 0, col*row*sizeof(gfele_t));
    } else {
       zcoomat_free(pcoomat);
       make_zero(&pcoomat->mat_val, row, newcol);
       pcoomat->lil_pos.data = (gfele_t*)calloc(1, row*newcol*sizeof(gfele_t));
       pcoomat->lil_pos.col = newcol;
    }

    for (i = 0; i < row; i++) {
        mat_node *p = mat_list_indentity[i].phead;
        j=0;
        while (p != NULL) {
            plil_pos->data[i*newcol+j] = p->pos;
            pmat_val->data[i*newcol+j] = p->value;
            j++;
            p = p->pnext;
        }
    }

    free_mat_list(mat_list_raw, row);
    free_mat_list(mat_list_indentity, row);
    free(mat_list_raw);
    free(mat_list_indentity);
    return 0;
}

int inverse_gfmat(gfmat_t *pgmat, gfm_t *gf)
{
    int i, j;
    int row = pgmat->row;
    int col = pgmat->col;

    head_t mat_list_raw[row];
    head_t mat_list_indentity[row];
    for (i = 0; i < row; i++) {
        mat_list_raw[i].len = 0;
        mat_list_raw[i].phead = NULL;
        mat_list_indentity[i].len = 0;
        mat_list_indentity[i].phead = NULL;
    }

    for (i = 0; i < row; i++) {
        for (j = 0; j < col; j++) {
            gfele_t value = pgmat->data[i*col+j];
            if (value) {
                mat_node *p =  set_mat_node(value, j);
                if (NULL == p) {
                    free_mat_list(mat_list_raw, row);
                    return -1;
                }
                list_append(&mat_list_raw[i], p);
            }
        }
    }

    if (inverse_implement(mat_list_raw, mat_list_indentity, row, gf)) {
        print_error("inverse error\n");
        show_mat_list(mat_list_raw, row);
        show_mat_list(mat_list_indentity, row);
        return -1;
    }

    for (i = 0; i < row; i++) {
        for (j = 0; j < col; j++) {
            pgmat->data[i*col+j] = 0;
        }
    }
    for (i = 0; i < row; i++) {
        mat_node *p = mat_list_indentity[i].phead;
        while (p != NULL) {
            pgmat->data[i*col+p->pos] = p->value;
            p = p->pnext;
        }
    }

    free_mat_list(mat_list_raw, row);
    free_mat_list(mat_list_indentity, row);
    return 0;
}


// inverse the lil_t matrix
// return: 0 on success
int inverse_lil(lil_t *pzlil, gfm_t *gf)
{
    int i, j;
    int row = pzlil->row;
    int col = pzlil->col;
    //gfmat_t *pmat_val = &(pcoomat->mat_val);
    lil_t *plil_pos = pzlil;

    head_t mat_list_raw[row];
    head_t mat_list_indentity[row];
    for (i = 0; i < row; i++) {
        mat_list_raw[i].len = 0;
        mat_list_raw[i].phead = NULL;
        mat_list_indentity[i].len = 0;
        mat_list_indentity[i].phead = NULL;
    }

    for (i = 0; i < row; i++) {
        for (j = 0; j < col; j++) {
            if (j!=0 && plil_pos->data[i*col+j]==0) {
                break;
            }
            mat_node *p =  set_mat_node(1, plil_pos->data[i*col+j]);
            if (NULL == p) {
                free_mat_list(mat_list_raw, row);
                return -1;
            }
            list_append(&mat_list_raw[i], p);
        }
    }

    if (inverse_implement(mat_list_raw, mat_list_indentity, row, gf)) {
        print_error("inverse error\n");
        return -1;
    }

    int newcol = col;
    for (i = 0; i < row; i++) {
        if (newcol < mat_list_indentity[i].len) {
            newcol = mat_list_indentity[i].len;
        }
    }
    //printf("newcol: %d\n", newcol);
    if (newcol == col) {
        memset(pzlil->data, 0, col*row*sizeof(gfele_t));
    } else {
        zlil_free(pzlil);
        pzlil->data = (gfele_t*)calloc(1, row*newcol*sizeof(gfele_t));
        pzlil->col = newcol;
    }
    //show_mat_list(mat_list_indentity, row);
    for (i = 0; i < row; i++) {
        mat_node *p = mat_list_indentity[i].phead;
        j = 0;
        while (p != NULL) {
            pzlil->data[i*newcol+j] = p->pos;
            j++;
            p = p->pnext;
        }
    }

    //print_lil(pzlil);
    free_mat_list(mat_list_raw, row);
    free_mat_list(mat_list_indentity, row);
    return 0;
}
