#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../file_operations.h"
#include "../coders.h"
#include "../crs.h"

void help(const char *file)
{
    printf("Usage: %s src_filename des_filepath [k n w packet_size]\n\n", file);
    printf("  src_filename:\t the file to be encode(./data.txt)\n");
    printf("  des_filepath:\t the path to store encode files(./data/)\n");
    printf("  k:\t\t data devices number(4)\n");
    printf("  m:\t\t parity devices number(2)\n");
    printf("  w:\t\t word unit(8/16/32)\n");
    printf("  packet_size:\t the process unit 1024B(>256B)\n");
}

int main(int argc, char const* argv[])
{
    int ret;
    crs_coder_t crs_code;
    const char *src_filename = "./test.txt";
    const char *des_filepath = "./data/";
    int k = 4;     // init to 4, data devices number
    int m = 2;     // init to 2, parity devices number
    int w = 4; // init to 4
    int packet_size = 1024; // init to 1k

    if (argc>1 && !strcmp(argv[1], "-h")) {
        help(argv[0]); 
        return -1;
    }
    if (argc>1) src_filename = argv[1];
    if (argc>2) des_filepath = argv[2];
    if (argc>3) k = atoi(argv[3]);
    if (argc>4) m = atoi(argv[4]);
    if (argc>5) w = atoi(argv[5]);
    if (argc>6) packet_size = atoi(argv[6]);

    // ---- encode ----
    // read data
    int data_len;
    data_len = get_filesize(src_filename);
    char *orig_data;
    orig_data = (char*)malloc(sizeof(char)*data_len);
    read_single_file(src_filename, data_len, orig_data);

    char *encoded_data, *encoded_parity;
    int chunk_len;
    ret = librlc_crs_encode(k, m, w, packet_size, orig_data, data_len,
            &encoded_data, &encoded_parity, &chunk_len);
    free(orig_data);
    orig_data = NULL;

    printf("crs encode return: %d, chunk_len: %d\n", ret, chunk_len);
    // store encoded data
    char *encode_data_filename = "./data/crs_encoded_data";
    write_2single_file(encode_data_filename, k*w*chunk_len, encoded_data);

    // store encode parity
    char *encode_parity_filename = "./data/crs_encoded_parity";
    write_2single_file(encode_parity_filename, m*w*chunk_len, encoded_parity);

    librlc_crs_encode_cleanup(encoded_data, encoded_parity);

    // ---- decode ----
    // set available data and list
    encoded_data = (char*)malloc(k*w*chunk_len);
    encoded_parity = (char*)malloc(m*w*chunk_len);
    read_single_file(encode_data_filename, k*w*chunk_len, encoded_data);
    read_single_file(encoded_parity, m*w*chunk_len, encoded_parity);
    int data_list[k*w];
    int i;
    for (i = 0; i < k*w-1; i++) {
        data_list[i] = i;
    }
    data_list[k*w-1] = k*w;
    char *available_data;
    char *out_data;
    available_data = encoded_data;
    memcpy(available_data+(k*w-1)*chunk_len, encoded_parity, chunk_len);
    librlc_crs_decode(k, m, w, packet_size, available_data, data_list, k*w,
            chunk_len, &out_data);
    char *decode_data_filename = "./data/crs_decoded_data";
    write_2single_file(decode_data_filename, data_len, out_data);
    librlc_crs_decode_cleanup(out_data);
    free(encoded_data);
    encoded_data = NULL;
    free(encoded_parity);
    encoded_parity = NULL;

    // ---- repair ----
    // set available data and list
    encoded_data = (char*)malloc(k*w*chunk_len);
    encoded_parity = (char*)malloc(m*w*chunk_len);
    read_single_file(encode_data_filename, k*w*chunk_len, encoded_data);
    read_single_file(encode_parity_filename, m*w*chunk_len, encoded_parity);
    for (i = 0; i < k*w-1; i++) {
        data_list[i] = i;
    }
    data_list[k*w-1] = k*w;
    available_data = encoded_data;
    memcpy(available_data+(k*w-1)*chunk_len, encoded_parity, chunk_len);

    // set repair list
    int repair_list[m*w];
    repair_list[0] = k*w-1;
    for (i = 1; i < m*w; i++) {
        repair_list[i]= i+k*w;
    }
    librlc_crs_repair(k, m, w, packet_size, available_data, data_list, k*w,
            chunk_len, repair_list, m*w, &out_data);
    char *repair_data_filename = "./data/crs_repair_data";
    memcpy(encoded_data+(k*w-1)*chunk_len, out_data, chunk_len);
    write_2single_file(repair_data_filename, k*w*chunk_len, encoded_data);

    char *repair_parity_filename = "./data/crs_repair_parity";
    memcpy(encoded_parity+chunk_len, out_data+chunk_len, (m*w-1)*chunk_len);
    write_2single_file(repair_parity_filename, m*w*chunk_len, encoded_parity);
    librlc_crs_repair_cleanup(out_data);
    free(encoded_data);
    encoded_data = NULL;
    free(encoded_parity);
    encoded_parity = NULL;

    return 0;
}
