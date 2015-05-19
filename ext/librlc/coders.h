#ifndef CODERS_H
#define CODERS_H

/**
 * coders interface for users, include:
 * 1. RS
 * 2. CRS
 */

// ---- RS code ----
int librlc_rs_encode(int k, int m, int w, int packet_size,
        const char *orig_data, int orig_data_len,
        char **encoded_data, char **encoded_parity,
        int *chunk_len);
int librlc_rs_encode_cleanup(char *encoded_data, char *encoded_parity);

int librlc_rs_decode(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int data_num,
        int chunk_len, char **out_data);

int librlc_rs_decode_cleanup(char *out_data);

int librlc_rs_repair(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int data_num,int chunk_len,
        int *repair_list, int repair_num, char **out_data);

int librlc_rs_repair_cleanup(char *out_data);

// ---- CRS code ----
int librlc_crs_encode(int k, int m, int w, int packet_size,
        const char *orig_data, int orig_data_len,
        char **encoded_data, char **encoded_parity,
        int *chunk_len);
int librlc_crs_encode_cleanup(char *encoded_data, char *encoded_parity);

int librlc_crs_decode(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int data_num,
        int chunk_len, char **out_data);

int librlc_crs_decode_cleanup(char *out_data);

int librlc_crs_repair(int k, int m, int w, int packet_size,
        char *available_data, int *data_list, int data_num,int chunk_len,
        int *repair_list, int repair_num, char **out_data);

int librlc_crs_repair_cleanup(char *out_data);

// ---- zcode ----
int librlc_z_encode(int k, int m, int packet_size,
        const char *orig_data, int orig_data_len,
        char **encoded_data, char **encoded_parity,
        int *chunk_len);
int librlc_z_encode_cleanup(char *encoded_data, char *encoded_parity);

int librlc_z_repair_chunk_needed(int m, int k, int node, int chunk_num,
        int *chunk_list);

int librlc_z_repair(int k, int m, int packet_size,
        char *available_data, int *data_list, int data_num,int chunk_len,
        int node, 
        char **out_data);

int librlc_z_repair_cleanup(char *out_data);

#endif
