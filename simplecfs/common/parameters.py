# -*- coding: utf-8 -*-
"""
define common used parameters for simplecfs
"""

# successful operation return
RET_SUCCESS = True

# failed operation return
RET_FAILURE = False

# ==== DS defined parameters ====

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

# ---- operation between client and mds ----
OP_MAKE_DIR = 'MAKE_DIR'
OP_MAKE_DIR_REPLY = 'MAKE_DIR_REPLY'
