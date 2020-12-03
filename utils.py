import threading

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.colors import ListedColormap

import constants as c
from alphabeta import alpha_beta_tt


def show(*data, size=3):
    palette = sns.color_palette("mako")
    uniqued = np.unique(data)
    # uniqued = np.delete(uniqued, np.where(uniqued > 20)
    vmin = 0
    vmax = 2 + max(np.delete(uniqued, np.where(uniqued > 20)))
    l = len(data)
    if l > 1:
        fig, axs = plt.subplots(1, l, figsize=(size * l, size))
        i = 0
        for ax in axs:
            sns.heatmap(data[i], annot=True, cbar=False, ax=ax, square=True, cmap=palette, robust=True, vmax=vmax)
            i += 1
    else:
        plt.figure(figsize=(size, size))
        sns.heatmap(data[0], annot=True, cbar=False, square=True, cmap=palette, robust=True, vmax=vmax)
    plt.show()


_b_colormap = ListedColormap(
    ["#7777AA", "#777777", "#000000", "#DDDDDD", "#DD4444"])


def show_board(k, w, b, size=3):
    p = w * 20
    p += k * 30
    p += b * 10
    p[p == 0] = c.BUILDINGS[p == 0] * -10
    plt.figure(figsize=(size, size))
    sns.heatmap(p, cmap=_b_colormap, annot=False, cbar=False, square=True)
    plt.show()


def generate_random_pawns(curr_tot_board, n_pawns):
    n = 0
    res = np.zeros((9, 9), dtype=bool)
    while n < n_pawns:
        pos = np.random.randint(0, 9), np.random.randint(0, 9)
        if not curr_tot_board[pos] and not res[pos]:
            res[pos] = True
            n += 1
    return res


def generate_random_state():
    k = generate_random_pawns(c.BOARD_CAMPS, 1)
    w = generate_random_pawns(c.BUILDINGS + k, 8)
    b = generate_random_pawns(c.BOARD_CASTLE + w + k, 16)
    return k, w, b


def initialize_jit():
    k, w, b = c.START_KING.copy(), c.START_WHITE.copy(), c.START_BLACK.copy()
    alpha_beta_tt(k, w, b, 1, float('-inf'), float('inf'), 'w', 1, threading.Event())
