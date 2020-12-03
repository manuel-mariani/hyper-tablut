import numpy as np
from numba.typed import Dict

from constants import BOARD_ESCAPES
from heuristics import heuristic
from metrics import pawn_count
from move_generation import generate_ordered_moves
from states import advance_state, get_capture_victims, apply_captures, revert_state, \
    revert_captures
from transpositions import tt_lookup, tt_ab, tt_set, tt_best_moves, zhash


def alpha_beta_tt(k, w, b, depth, alpha, beta, color, max_depth, timeout_event):
    if timeout_event.isSet():
        return None, None

    # Terminal cases
    if np.any(k * BOARD_ESCAPES):
        return +3.4028235e+38 / (1 + max_depth - depth), None
    if not np.any(k):
        return -3.4028235e+38 / (1 + max_depth - depth), None
    if pawn_count(b) == 0:
        return +3.4028235e+30 / (1 + max_depth - depth), None
    if pawn_count(w) == 0 and np.any(k * BOARD_ESCAPES):
        return -3.4028235e+30 / (1 + max_depth - depth), None

    # Transposition table lookup
    best_move = None
    tt_entry = tt_lookup(k, w, b, tt_ab)
    if tt_entry is not None and tt_entry.get('depth', float('-inf')) >= depth:
        lowerbound = tt_entry.get('lowerbound', float('-inf'))
        upperbound = tt_entry.get('upperbound', float('+inf'))
        best_move = tt_best_moves.get(zhash(k, w, b), None)
        if lowerbound >= beta:
            return lowerbound, best_move
        if upperbound <= alpha:
            return upperbound, best_move
        alpha = max(alpha, lowerbound)
        beta = min(beta, upperbound)
    alpha_orig = alpha
    beta_orig = beta

    # Max depth reached (leaf node)
    if depth == 0:
        return heuristic(k, w, b, depth, max_depth, tt_ab), best_move

    # Move generation and ordering
    ordered_moves = generate_ordered_moves(k, w, b, color, depth, max_depth)

    best_move = None
    if color == 'w':  # MAXNODE
        best_value = float('-inf')
        for origin, destination, _ in ordered_moves:
            advance_state(k, w, b, origin, destination)
            captures = get_capture_victims(k, w, b, color, destination)
            apply_captures(k, w, b, captures)
            value, _ = alpha_beta_tt(k, w, b, depth - 1, alpha, beta, 'b', max_depth, timeout_event)
            revert_state(k, w, b, origin, destination)
            revert_captures(k, w, b, captures)

            if timeout_event.isSet():
                return None, None
            if value > best_value:
                best_value = value
                best_move = (origin, destination)
            if best_value > alpha:
                alpha = best_value
            if alpha > beta:
                break

    else:  # MINNODE
        best_value = float('+inf')
        for origin, destination, _ in ordered_moves:
            advance_state(k, w, b, origin, destination)
            captures = get_capture_victims(k, w, b, color, destination)
            apply_captures(k, w, b, captures)
            value, _ = alpha_beta_tt(k, w, b, depth - 1, alpha, beta, 'w', max_depth, timeout_event)
            revert_state(k, w, b, origin, destination)
            revert_captures(k, w, b, captures)

            if timeout_event.isSet():
                return None, None
            if value < best_value:
                best_value = value
                best_move = (origin, destination)
            if best_value < beta:
                beta = best_value
            if alpha > beta:
                break

    # Transposition table storing
    tt_entry_data = Dict()
    if best_value <= alpha_orig:
        tt_entry_data['upperbound'] = best_value
        tt_entry_data['lowerbound'] = float('-inf')
    elif alpha_orig < best_value < beta_orig:
        tt_entry_data['upperbound'] = best_value
        tt_entry_data['lowerbound'] = best_value
    else:
        tt_entry_data['upperbound'] = float('+inf')
        tt_entry_data['lowerbound'] = best_value
    tt_entry_data['depth'] = depth
    tt_best_moves[zhash(k, w, b)] = best_move
    tt_set(k, w, b, tt_entry_data, tt_ab)

    return best_value, best_move
