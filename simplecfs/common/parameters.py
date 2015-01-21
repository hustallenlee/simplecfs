# -*- coding: utf-8 -*-
"""
define common used parameters for simplecfs
"""

# successful operation return
RET_SUCCESS = 0

# failed operation return
RET_FAILURE = -1

# ==== DS defined parameters ====

# chunk state
CHUNK_OK = 1000
CHUNK_MISSING = 1001
CHUNK_BREAK = 1002   # when DS is break
# CHUNK_DAMAGED = 1003

# data send and recv frame size
DATA_FRAME_SIZE = 8192  # 8K

# ==== operations ====
OP_ADD_CHUNK = 'ADD_CHUNK'
OP_ADD_CHUNK_REPLY = 'ADD_CHUNK_REPLY'

OP_DELETE_CHUNK = 'DELETE_CHUNK'
OP_DELETE_CHUNK_REPLY = 'DELETE_CHUNK_REPLY'
