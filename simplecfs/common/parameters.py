# -*- coding: utf-8 -*-
"""
define common used parameters for simplecfs
"""

# successful operation return
RET_SUCCESS = True

# failed operation return
RET_FAILURE = False

# ==== DS defined parameters ====

# ds state
DS_CONNECTED = 'OK'
DS_BROKEN = 'FAILED'

# chunk state
CHUNK_OK = 1000
CHUNK_MISSING = 1001
CHUNK_BREAK = 1002   # when DS is break
# CHUNK_DAMAGED = 1003

# data send and recv frame size
DATA_FRAME_SIZE = 8192  # 8K

# ==== operations ====

# ---- operations between client and ds
OP_ADD_CHUNK = 'ADD_CHUNK'
OP_ADD_CHUNK_REPLY = 'ADD_CHUNK_REPLY'

OP_DELETE_CHUNK = 'DELETE_CHUNK'
OP_DELETE_CHUNK_REPLY = 'DELETE_CHUNK_REPLY'

OP_GET_CHUNK = 'GET_CHUNK'
OP_GET_CHUNK_REPLY = 'GET_CHUNK_REPLY'

# ---- operations between ds and mds
OP_ADD_DS = 'ADD_DS'
OP_ADD_DS_REPLY = 'ADD_DS_REPLY'

OP_CHECK_CHUNK = 'CHECK_CHUNK'
OP_CHECK_CHUNK_REPLY = 'CHECK_CHUNK_REPLY'

OP_REPORT_DS = 'REPORT_DS'
OP_REPORT_DS_REPLY = 'REPORT_DS_REPLY'

# ---- operation between client and mds ----
OP_MAKE_DIR = 'MAKE_DIR'
OP_MAKE_DIR_REPLY = 'MAKE_DIR_REPLY'

OP_REMOVE_DIR = 'REMOVE_DIR'
OP_REMOVE_DIR_REPLY = 'REMOVE_DIR_REPLY'

OP_LIST_DIR = 'LIST_DIR'
OP_LIST_DIR_REPLY = 'LIST_DIR_REPLY'

OP_STATUS_DIR = 'STATUS_DIR'
OP_STATUS_DIR_REPLY = 'STATUS_DIR_REPLY'

OP_VALID_DIR = 'VALID_DIR'
OP_VALID_DIR_REPLY = 'VALID_DIR_REPLY'
