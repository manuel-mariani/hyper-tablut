import numpy as np
from numba import jit

from constants import BUILDINGS, CAMPS_SUBGROUPS_II, XOR_CAMPS_SUBGROUPS
from heuristics import heuristic
from states import advance_state, get_capture_victims, apply_captures, revert_state, revert_captures
from transpositions import tt_ab


@jit(nopython=True, fastmath=False, cache=False)
def generate_moves(pawn_board, total_board, color):
    moves = []
    obstacles = total_board + BUILDINGS
    for o_row, o_col in np.argwhere(pawn_board):
        # If the player is black and the pawn is in the camps, allow movement through camps
        if color == 'b':
            found = False
            for i in range(4):
                if CAMPS_SUBGROUPS_II[i, o_row, o_col]:
                    tmp_buildings = XOR_CAMPS_SUBGROUPS[i]
                    obstacles = total_board + tmp_buildings
                    found = True
            if not found:
                obstacles = total_board + BUILDINGS

        # loop through orthogonal positions (relative to pawn's) and break on an obstacle
        for rows in range(o_row - 1, -1, -1), range(o_row + 1, 9):
            for d_row in rows:
                if obstacles[d_row, o_col]:
                    break
                moves.append(((o_row, o_col), (d_row, o_col)))
        for cols in range(o_col - 1, -1, -1), range(o_col + 1, 9):
            for d_col in cols:
                if obstacles[o_row, d_col]:
                    break
                moves.append(((o_row, o_col), (o_row, d_col)))
    return moves


@jit(nopython=True, fastmath=True, cache=True)
def generate_player_moves(k, w, b, color):
    total = k + w + b
    if color == 'b':
        return generate_moves(b, total, 'b')
    if color == 'w':
        w_moves = generate_moves(w, total, 'w')
        k_moves = generate_moves(k, total, 'w')
        return k_moves + w_moves


def generate_ordered_moves(k, w, b, color, depth, max_depth):
    possible_moves = generate_player_moves(k, w, b, color)
    ordered_moves = []
    reverse = False if color == 'w' else False

    if depth > 1:  # FIXME
        for origin, destination in possible_moves:
            advance_state(k, w, b, origin, destination)
            captures = get_capture_victims(k, w, b, color, destination)
            apply_captures(k, w, b, captures)
            ordered_moves.append((origin, destination, heuristic(k, w, b, depth, max_depth, tt_ab)))
            revert_state(k, w, b, origin, destination)
            revert_captures(k, w, b, captures)
        ordered_moves = sorted(ordered_moves, key=lambda x: x[2], reverse=reverse)
        # if len(ordered_moves) > 40:
        #     ordered_moves = ordered_moves[0:40]
    else:
        for origin, destination in possible_moves:
            ordered_moves.append((origin, destination, 0))

    return ordered_moves


_KING_ESCAPE_POSITIONS = ((0, 1), (0, 2), (0, 6), (0, 7),
                          (1, 0), (2, 0), (6, 0), (7, 0),
                          (1, 8), (2, 8), (6, 8), (7, 8),
                          (8, 1), (8, 2), (8, 6), (8, 7))
