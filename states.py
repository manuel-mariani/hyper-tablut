from numba import jit
from numba.typed import List

from constants import *


# ---------- STATE ADVANCEMENT / MOVE APPLICATION -----------
@jit(nopython=True, fastmath=True, cache=True)
def advance_state(k, w, b, origin, destination):
    for pawns in k, w, b:
        if pawns[origin]:
            pawns[origin] = False
            pawns[destination] = True
            return


@jit(nopython=True, fastmath=True, cache=True)
def revert_state(k, w, b, origin, destination):
    advance_state(k, w, b, destination, origin)


# ---------- CAPTURES HANDLING -----------
@jit(nopython=True, fastmath=True, cache=True)  # TODO: parallel=True
def get_capture_victims(k, w, b, color, move_destination):
    king_victims = List()
    white_victims = List()
    black_victims = List()
    # Define allies and enemies based on the player's color
    white_side = k + w
    if color == 'w':
        allies, enemies = white_side, b
    else:
        allies, enemies = b, white_side

    md = tuple(move_destination)
    row_att, col_att = md
    for drv, drc in ((0, -1), (-1, 0), (0, 1), (1, 0)):
        row_vic, col_vic = row_att + drv, col_att + drc  # Position of victim pawn (next to the attacker)
        row_adj, col_adj = row_vic + drv, col_vic + drc  # Position of pawn next to the victim
        # Check bounds
        oob = False
        for v in row_vic, col_vic, row_adj, col_adj:
            if v < 0 or v > 8:
                oob = True
                break
        if oob:
            continue
        # Check if the victim is an enemy and if the adjacent is an ally or a building
        if not enemies[row_vic, col_vic]:
            continue
        if not (allies[row_adj, col_adj] or BUILDINGS[row_adj, col_adj]):
            continue
        vic_pos = np.array((row_vic, col_vic))

        if color == 'w':  # If attacker is white
            if (row_adj, col_adj) in [(4, 0), (4, 8), (0, 4), (8, 4)]:
                continue  # this skips the "inner" black camp as adjacent
            if b[row_vic, col_vic]:
                black_victims.append(vic_pos)
            continue
        # Else the attacker is black and the victim is a white soldier
        if w[row_vic, col_vic]:
            white_victims.append(vic_pos)
            continue
        # Else the attacker is black and the victim is the king
        # check if king is in a safe position (near or in castle)
        kings_safe_pos = ((4, 3), (3, 4), (4, 5), (5, 4), (4, 4))
        is_k_near_castle = (row_vic, col_vic) in kings_safe_pos
        is_k_captured = True
        # If king is near castle, check all of its side for threats
        if is_k_near_castle:
            for dr, dc in _CAPTURE_DELTA_WINDOW:
                row, col = row_vic + dr, col_vic + dc
                is_k_captured = is_k_captured and (BOARD_CASTLE[row, col] or b[row, col])

        if is_k_captured:
            # make king uncapturable if it's in the escape position [used for ai purposes]
            if (row_vic, col_vic) not in ESCAPE_POSITIONS:
                king_victims.append(vic_pos)

    return king_victims, white_victims, black_victims


@jit(nopython=True, fastmath=True, cache=True)
def apply_captures(k, w, b, capture_list, new_val=False):
    board = (k, w, b)
    for i in (0, 1, 2):
        for capture_pos in capture_list[i]:
            board[i][capture_pos[0], capture_pos[1]] = new_val


@jit(nopython=True, fastmath=True, cache=True)
def revert_captures(k, w, b, capture_list):
    apply_captures(k, w, b, capture_list, True)


_CAPTURE_DELTA_WINDOW = ((0, -1), (-1, 0), (0, 1), (1, 0))
