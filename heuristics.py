import numpy as np
from numba import jit, types
from numba.typed import Dict

from constants import BOARD_ESCAPES
from metrics import pawn_count, safeness, rook_distance_board, king_confinement, pawn_quadrant_uniformity
from transpositions import tt_lookup, tt_set


@jit(nopython=True, fastmath=True, parallel=True, cache=True)
def heuristic(k, w, b, depth, max_depth, tt):
    if np.any(k * BOARD_ESCAPES):
        return +3.4028235e+38 / (1 + max_depth - depth)
    if not np.any(k):
        return -3.4028235e+38 / (1 + max_depth - depth)
    if pawn_count(b) == 0:
        return +3.4028235e+30 / (1 + max_depth - depth)
    if pawn_count(w) == 0 and np.any(k * BOARD_ESCAPES):
        return -3.4028235e+30 / (1 + max_depth - depth)

    tt_dict = tt_lookup(k, w, b, tt)
    if tt_dict is not None:
        stored_value = tt_dict.get('heuristic', None)
        if stored_value is not None:
            return stored_value

    rook_dist_king = rook_distance_board(k, w + b, 'w')
    rook_dist_white = rook_distance_board(w, b + k, 'w')
    rook_dist_black = rook_distance_board(b, k + w, 'b')

    min_king_confinement = king_confinement(k, w, b,
                                            rook_dist_king)  # The lower the better (4 white); values in (0, 50]

    king_safeness = safeness(k, rook_dist_black, 'k')  # Higher: better for white values in [0, K_UNREACH(50)]
    white_safeness = safeness(w, rook_dist_black, 'w') / 8  # Higher: better for white; values in [0, K_UNREACH(50)]
    black_safeness = safeness(b, rook_dist_white, 'b') / 16  # Lower : better for white; values in [0, K_UNREACH(50)]

    pawn_difference = 2 * pawn_count(w) - pawn_count(b)  # Higher: better for white; values in [-16, 16]
    uniformity_difference = pawn_quadrant_uniformity(w) - pawn_quadrant_uniformity(b)
    safeness_difference = white_safeness - black_safeness  # Higher: better for white; values in [-K_UNREACH(-50), +K_UNREACH(50)]

    h = -2.5 * min_king_confinement + 1 * pawn_difference + 0.05 * safeness_difference + 0.05 * uniformity_difference + 0.002 * king_safeness

    # tempo = (100+depth) / (99 + max_depth)
    # h *= tempo

    tt_entry = Dict.empty(key_type=types.unicode_type, value_type=types.float64)
    tt_entry['heuristic'] = h
    tt_set(k, w, b, tt_entry, tt)
    return h
