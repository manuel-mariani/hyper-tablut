import numpy as np
from numba import jit

from constants import ESCAPE_POSITIONS, BUILDINGS

K_BUILDINGS = 50
K_UNREACH = 50
K_PAWNS = 25


@jit(nopython=True, fastmath=True, parallel=True, cache=True)
def rook_distance_board(pawns, other_pawns, color, buildings=BUILDINGS, max_iterations=5):
    rkd = np.full((9, 9), K_UNREACH)
    for row in range(9):
        for col in range(9):
            if pawns[row, col]:
                rkd[row, col] = 0
                continue
            if buildings[row, col]:
                rkd[row, col] = K_BUILDINGS
                continue
            if other_pawns[row, col]:
                rkd[row, col] = K_PAWNS
    obstacles = other_pawns + buildings
    for ci in range(1, max_iterations + 1):
        for pos_row in range(9):
            for pos_col in range(9):
                if rkd[pos_row, pos_col] != ci - 1:
                    continue
                for rows in range(pos_row - 1, -1, -1), range(pos_row + 1, 9):
                    for row in rows:
                        if rkd[row, pos_col] < ci or obstacles[row, pos_col]:
                            break
                        rkd[row, pos_col] = ci
                for cols in range(pos_col - 1, -1, -1), range(pos_col + 1, 9):
                    for col in cols:
                        if rkd[pos_row, col] < ci or obstacles[pos_row, col]:
                            break
                        rkd[pos_row, col] = ci
    return rkd


@jit(nopython=True, fastmath=True, cache=True)
def safeness(pawns, enemy_rkm, pawntype):
    tot_safeness = 0

    if pawntype == 'k':
        danger_buildings_positions = [(0, 3), (0, 5), (1, 4),
                                      (3, 0), (5, 0), (4, 1),
                                      (3, 8), (5, 8), (4, 7),
                                      (8, 3), (8, 5), (7, 4)]
    else:
        danger_buildings_positions = [(0, 3), (0, 5), (1, 4),
                                      (3, 0), (5, 0), (4, 1),
                                      (3, 8), (5, 8), (4, 7),
                                      (8, 3), (8, 5), (7, 4), (4, 4)]
    for pos_row, pos_col in np.argwhere(pawns):
        h_safeness, v_safeness = 0, 0
        for d_row in (1, -1):
            row = pos_row + d_row
            if 0 <= row <= 8:
                if (row, pos_col) in danger_buildings_positions:
                    curr_safeness = 0
                else:
                    curr_safeness = enemy_rkm[row, pos_col]
            else:  # out of bounds
                curr_safeness = K_PAWNS
            v_safeness += curr_safeness
        for d_col in (-1, 1):
            col = pos_col + d_col
            if 0 <= col <= 8:
                if (pos_row, col) in danger_buildings_positions:
                    curr_safeness = 0
                else:
                    curr_safeness = enemy_rkm[pos_row, col]
            else:  # out of bounds
                curr_safeness = K_PAWNS
            h_safeness += curr_safeness
        tot_safeness += min(h_safeness, v_safeness)
    return tot_safeness


@jit(nopython=True, fastmath=True, cache=True)
def king_confinement(k, w, b, king_rk):
    first_min = K_UNREACH + 1
    second_min = K_UNREACH + 1
    for ep in ESCAPE_POSITIONS:
        val = king_rk[ep]
        if val <= first_min and not w[ep]:
            second_min = first_min
            first_min = val
    return 0.8 * first_min + 0.2 * second_min


@jit(nopython=True, fastmath=True, cache=True)
def pawn_count(pawn_board):
    return np.sum(pawn_board)


@jit(nopython=True, fastmath=True)
def pawn_quadrant_uniformity(pawns):
    top_lx = np.sum(pawns[0:4, 0:4])
    top_rx = np.sum(pawns[0:4, 5:9])
    bot_lx = np.sum(pawns[5:9, 0:4])
    bot_rx = np.sum(pawns[5:9, 5:9])

    top_bot = abs(top_lx + top_rx - bot_lx - bot_rx)
    lef_rig = abs(top_lx + bot_lx - bot_rx - top_rx)
    return abs(top_bot - lef_rig)
