import threading
import time

from alphabeta import alpha_beta_tt
from heuristics import heuristic
from move_generation import generate_ordered_moves
from states import MAX_DEPTH, DEFAULT_TIMEOUT
from transpositions import tt_ab


def iterative_deepening_best_move(k, w, b, color, timeout=DEFAULT_TIMEOUT):
    move = [None]
    # Start a thread for iterative deepening
    start_time = time.time()
    timeout_event = threading.Event()
    thread_iterdeep = threading.Thread(target=_iterative_worker_mtd, args=(k, w, b, color, move, timeout_event))
    thread_iterdeep.start()
    thread_iterdeep.join(0.90 * timeout)
    if thread_iterdeep.is_alive():
        timeout_event.set()
    thread_iterdeep.join(0.05 * timeout)
    end_time = time.time()

    if move[0] is None:
        print("OVERRIDE: NONE MOVE DETECTED!")
        move[0] = generate_ordered_moves(k, w, b, color, 1, 1)[0][0:2]
    print("Time elapsed : %s" % (end_time - start_time), "thread_alive:", thread_iterdeep.is_alive())
    return move[0]


def _iterative_worker_ab(k, w, b, color, best_move_list, timeout_event: threading.Event):
    for depth in range(1, MAX_DEPTH + 1):
        guess, best_move = alpha_beta_tt(k, w, b, depth, float('-inf'), float('+inf'), color, depth, timeout_event)
        if timeout_event.isSet():
            break
        if best_move is not None:
            best_move_list[0] = best_move
        print(color, depth, best_move_list[0], guess)


def _iterative_worker_mtd(k, w, b, color, best_move_list, timeout_event):
    guess = heuristic(k, w, b, 0, 0, tt_ab)
    i = 0
    for depth in range(2, MAX_DEPTH + 2):
        curr_guess, best_move = mtdf(k, w, b, depth, guess, color, timeout_event)
        if timeout_event.isSet():
            break
        if best_move is not None:
            best_move_list[0] = best_move
        i += 1
        if i % 2 == 0:
            guess = curr_guess
        print(color, depth, best_move_list[0], guess)


def mtdf(k, w, b, max_depth, first_guess, color, timeout_event):
    guess = first_guess
    upperbound = float('+inf')
    lowerbound = float('-inf')
    move = None
    i = 0
    window = 1
    while lowerbound < upperbound:
        if guess == lowerbound:
            beta = guess + window
        else:
            beta = guess

        # print("MTDF, iteration: ", i, "GUESS:", guess, "BETA:", beta, "UPPERBOUND:", upperbound, "LOWERBOUND",
        #       lowerbound)

        curr_guess, curr_move = alpha_beta_tt(k, w, b, max_depth, beta - window, beta, color, max_depth, timeout_event)
        if timeout_event.isSet():
            return guess, move

        guess = curr_guess
        move = curr_move

        i += 1
        if not (-1e10 < guess < 1e10):
            break
        if guess < beta:
            upperbound = guess
        else:
            lowerbound = guess
    return guess, move
