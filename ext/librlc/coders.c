#include "coders.h"
#include "rs.h"
#include "crs.h"
#include "zcode.h"

// RS -----------

int librlc_rs_encode(int k, int m, int w, int packet_size,
        const char *orig_data, int orig_data_len,
        char **encoded_data, char **encoded_parity,
        int *chunk_len)
{
    rs_coder_t rs_code;
    // rs init
    rs_init(&rs_code, k+m, k, w, packet_size);
    // rs encode
    rs_encode(rs_code.prsi, orig_data, orig_data_len, encoded_data, encoded_parity, chunk_len);

    // rs free
    rs_free(&rs_code);

    return 0;
}

int librlc_rs_encode_cleanup(char *encoded_data, char *encoded_parity)
{
    free(encoded_data);
    free(encoded_parity);

    return 0;
}

int librlc_rs_decode(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int chunk_num,
        int chunk_len, char **out_data)
{
    int ret = 0;
    rs_coder_t rs_code;
    // rs init
    rs_init(&rs_code, k+m, k, w, packet_size);
    // rs decode
    ret = rs_decode(rs_code.prsi, available_data, data_list, chunk_num, chunk_len, out_data);

    // rs free
    rs_free(&rs_code);

    return ret ;
}

int librlc_rs_decode_cleanup(char *out_data)
{
    free(out_data);
    return 0;
}

int librlc_rs_repair(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int data_num,int chunk_len,
        int *repair_list, int repair_num, char **out_data)
{
    int ret = 0;
    rs_coder_t rs_code;
    //rs init
    rs_init(&rs_code, k+m, k, w, packet_size);
    // re repair
    ret = rs_repair(rs_code.prsi, available_data, data_list, data_num,
            chunk_len, repair_list, repair_num, out_data);

    // rs free
    rs_free(&rs_code);
    return ret;
}

int librlc_rs_repair_cleanup(char *out_data)
{
    free(out_data);
    return 0;
}

// CRS -----------------------
int librlc_crs_encode(int k, int m, int w, int packet_size,
        const char *orig_data, int orig_data_len,
        char **encoded_data, char **encoded_parity,
        int *chunk_len)
{
    crs_coder_t crs_code;
    // crs init
    crs_init(&crs_code, k+m, k, w, packet_size);
    // rs encode
    crs_encode(crs_code.pcrsi, orig_data, orig_data_len, encoded_data, encoded_parity, chunk_len);

    // rs free
    crs_free(&crs_code);

    return 0;
}

int librlc_crs_encode_cleanup(char *encoded_data, char *encoded_parity)
{
    free(encoded_data);
    free(encoded_parity);

    return 0;
}

int librlc_crs_decode(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int chunk_num,
        int chunk_len, char **out_data)
{
    int ret = 0;
    crs_coder_t crs_code;
    // crs init
    crs_init(&crs_code, k+m, k, w, packet_size);
    // crs decode
    ret = crs_decode(crs_code.pcrsi, available_data, data_list, chunk_num, chunk_len, out_data);

    // crs free
    crs_free(&crs_code);

    return ret ;
}

int librlc_crs_decode_cleanup(char *out_data)
{
    free(out_data);
    return 0;
}

int librlc_crs_repair(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int data_num,int chunk_len,
        int *repair_list, int repair_num, char **out_data)
{
    int ret = 0;
    crs_coder_t crs_code;
    //crs init
    crs_init(&crs_code, k+m, k, w, packet_size);
    // re repair
    ret = crs_repair(crs_code.pcrsi, available_data, data_list, data_num,
            chunk_len, repair_list, repair_num, out_data);

    // crs free
    crs_free(&crs_code);
    return ret;
}

int librlc_crs_repair_cleanup(char *out_data)
{
    free(out_data);
    return 0;
}

// zcode --------------
int librlc_z_encode(int k, int m, int packet_size,
        const char *orig_data, int orig_data_len,
        char **encoded_data, char **encoded_parity,
        int *chunk_len)
{
    z_coder_t z_code;
    // z init
    z_init(&z_code, m, k, packet_size);
    // z encode
    int ret = z_encode(z_code.pzi, orig_data, orig_data_len, encoded_data, encoded_parity, chunk_len);

    // rs free
    z_free(&z_code);

    return ret;
}

int librlc_z_encode_cleanup(char *encoded_data, char *encoded_parity)
{
    free(encoded_data);
    free(encoded_parity);

    return 0;
}

int librlc_z_repair_chunk_needed(int m, int k, int node, int chunk_num,
        int *chunk_list)
{
    int ret = z_repair_chunk_needed(m, k, node, chunk_num, chunk_list);
    return ret;
}

int librlc_z_repair(int k, int m, int packet_size,
        char *available_data, int *data_list, int data_num,int chunk_len,
        int node, 
        char **out_data)
{
    int ret = 0;
    z_coder_t z_code;
    //z init
    z_init(&z_code, m, k, packet_size);
    // re repair
    ret = z_repair(z_code.pzi, available_data, data_list, data_num,
            chunk_len, node, out_data);

    // z free
    z_free(&z_code);
    return ret;
}

int librlc_z_repair_cleanup(char *out_data)
{
    free(out_data);
    return 0;
}
