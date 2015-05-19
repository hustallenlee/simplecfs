#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../file_operations.h"
#include "../coders.h"
#include "../zcode.h"

void help(const char *file)
{
    printf("Usage: %s src_filename des_filepath [m k node packet_size]\n\n", file);
    printf("  src_filename:\t the file to be encode(./data.txt)\n");
    printf("  des_filepath:\t the path to store encode files(./data/)\n");
    printf("  m:\t\t parity devices number(2)\n");
    printf("  k:\t\t data devices number(4)\n");
    printf("  node:\t\t node to repair(0, < k)\n");
    printf("  packet_size:\t the process unit 1024B(>256B)\n");
}

int main(int argc, char const* argv[])
{
    int ret;
    z_coder_t z_code;
    const char *src_filename = "./test.txt";
    const char *des_filepath = "./data/";
    int m = 2;     // init to 2, parity devices number
    int k = 4;     // init to 4, data devices number
    int node = 0; // init to 0
    int packet_size = 1024; // init to 1k

    if (argc>1 && !strcmp(argv[1], "-h")) {
        help(argv[0]); 
        return -1;
    }
    if (argc>1) src_filename = argv[1];
    if (argc>2) des_filepath = argv[2];
    if (argc>3) m = atoi(argv[3]);
    if (argc>4) k = atoi(argv[4]);
    if (argc>5) node = atoi(argv[5]);
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
    ret = librlc_z_encode(k, m, packet_size, orig_data, data_len,
            &encoded_data, &encoded_parity, &chunk_len);
    free(orig_data);
    orig_data = NULL;

    printf("z encode return: %d, chunk_len: %d\n", ret, chunk_len);
    int r = ZMAT_R(m, k);
    // store encoded data
    char *encode_data_filename = "./data/z_encoded_data";
    write_2single_file(encode_data_filename, k*r*chunk_len, encoded_data);

    // store encode parity
    char *encode_parity_filename = "./data/z_encoded_parity";
    write_2single_file(encode_parity_filename, m*r*chunk_len, encoded_parity);

    librlc_z_encode_cleanup(encoded_data, encoded_parity);

    // ---- decode ----
    // no decode in zcode , use original data to decode data
    char *decode_data_filename = "./data/z_decoded_data";
    write_2single_file(decode_data_filename, data_len, encoded_data);

    // ---- repair ----
    // set available data and list
    encoded_data = (char*)malloc(k*r*chunk_len);
    encoded_parity = (char*)malloc(m*r*chunk_len);
    read_single_file(encode_data_filename, k*r*chunk_len, encoded_data);
    read_single_file(encode_parity_filename, m*r*chunk_len, encoded_parity);

    // set repair list
    int repair_num = (m+k-1)*r/m;
    int repair_list[repair_num];
    librlc_z_repair_chunk_needed(m, k, node, repair_num, repair_list);
    
    // set available data
    char *available_data = (char*)malloc(repair_num*chunk_len);
    int i;
    for (i = 0; i < (k-1)*r/m; i++) {
        memcpy(available_data+(i*chunk_len), encoded_data+(repair_list[i]*chunk_len), chunk_len);
    }
    for (i = (k-1)*r/m; i < (m+k-1)*r/m; i++) {
        memcpy(available_data+(i*chunk_len), encoded_parity+((repair_list[i]-k*r)*chunk_len), chunk_len);
    }

    char *out_data;
    ret = librlc_z_repair(k, m, packet_size, available_data, repair_list, repair_num,
            chunk_len, node, &out_data);

    char *repair_data_filename = "./data/z_repair_data";
    memcpy(encoded_data+(node*r)*chunk_len, out_data, r*chunk_len);
    write_2single_file(repair_data_filename, k*r*chunk_len, encoded_data);

    librlc_z_repair_cleanup(out_data);
    free(encoded_data);
    encoded_data = NULL;
    free(encoded_parity);
    encoded_parity = NULL;
    free(available_data);
    available_data = NULL;

    return 0;
}
