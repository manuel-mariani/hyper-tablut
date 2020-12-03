# %%

import numpy as np
from numba import jit, types
from numba.typed import Dict

np.random.seed(0)
_randargs = {"high": np.iinfo(np.uint64).max, "dtype": np.uint64, "size": (2, 4, 9, 9)}

zobrist_table_k = np.random.randint(0, **_randargs)
zobrist_table_w = np.random.randint(0, **_randargs)
zobrist_table_b = np.random.randint(0, **_randargs)
for zt in zobrist_table_k, zobrist_table_w, zobrist_table_b:
    for rot in (1, 2, 3):
        zt[0, rot] = np.rot90(zt[0, rot - 1])
    for rot in (0, 1, 2, 3):
        zt[1, rot] = np.fliplr(zt[0, rot])


@jit(nopython=True, fastmath=True)
def zhash(k, w, b, flip=0, rot=0):
    h = np.uint64(0)  # np.zeros(1, dtype=np.uint64)
    ztk = zobrist_table_k[flip, rot]
    ztw = zobrist_table_w[flip, rot]
    ztb = zobrist_table_b[flip, rot]
    for row in range(9):
        for col in range(9):
            if k[row, col]:
                h = np.bitwise_xor(h, ztk[row, col])
            if w[row, col]:
                h = np.bitwise_xor(h, ztw[row, col])
            if b[row, col]:
                h = np.bitwise_xor(h, ztb[row, col])
    return h


@jit(nopython=True)
def hyper_hash(k, w, b):
    hash_values = []
    for flip in (0, 1):
        for rot in (0, 1, 2, 3):
            hash_values.append(zhash(k, w, b, flip, rot))
    hash_array = np.array(hash_values)
    return hash_array


tt_ab = Dict.empty(
    key_type=types.uint64,
    value_type=types.DictType(types.unicode_type, types.float64)
)
# transposition_table = dict()
tt_best_moves = {}


@jit(nopython=True)
def tt_lookup(k, w, b, tt):
    h = zhash(k, w, b)
    if h in tt:
        return tt[h]
    else:
        return None


@jit(nopython=True)
def tt_set(k, w, b, entry, tt):
    # hh = hyper_hash(k, w, b)
    # for h in hh:
    h = zhash(k, w, b)
    if h not in tt:
        tt[h] = entry
    else:
        for k in entry.keys():
            tt[h][k] = entry[k]
