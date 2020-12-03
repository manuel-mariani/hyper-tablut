import pygame
import pygame.freetype
from pygame import gfxdraw

import states
from constants import START_KING, START_WHITE, START_BLACK, BUILDINGS
from iterative_deepening import iterative_deepening_best_move

_WINDOW_SIZE = 450
_GRID_SIZE = _WINDOW_SIZE // 9


class TablutGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((_WINDOW_SIZE, _WINDOW_SIZE))
        pygame.display.set_caption("Tablut")
        pygame.freetype.init()
        self.font = pygame.freetype.SysFont("Arial", 20)
        self.isRunning = True

    def loop_no_events(self):
        k = START_KING.copy()
        w = START_WHITE.copy()
        b = START_BLACK.copy()
        state = k, w, b
        while self.isRunning:
            self.draw(*state, 'w')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

    def loop_interactive(self, player_color, ai_color):
        assert player_color in ('w', 'b') and ai_color in ('w', 'b') and player_color != ai_color
        k = START_KING.copy()
        w = START_WHITE.copy()
        b = START_BLACK.copy()
        state = k, w, b
        move_origin = None
        move_destin = None
        while self.isRunning:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False
                if event.type == pygame.MOUSEBUTTONUP:
                    coord = coord = (mouse_pos[1] // _GRID_SIZE, mouse_pos[0] // _GRID_SIZE)
                    if move_origin is None:
                        move_origin = coord
                    elif move_destin is None:
                        move_destin = coord
                        states.advance_state(k, w, b, move_origin, move_destin)
                        captures = states.get_capture_victims(k, w, b, color=player_color, move_destination=move_destin)
                        states.apply_captures(k, w, b, captures)

                        move_origin = None
                        move_destin = None
                        self.draw(*state, None, mouse_pos, move_origin)
                        ai_move = iterative_deepening_best_move(k, w, b, ai_color)
                        states.advance_state(k, w, b, *ai_move)
                        states.apply_captures(k, w, b, states.get_capture_victims(k, w, b, ai_color, ai_move[1]))
            self.draw(*state, None, mouse_pos, move_origin)

    def loop_ai(self, k_start=START_KING.copy(), w_start=START_WHITE.copy(), b_start=START_BLACK.copy()):
        k = k_start
        w = w_start
        b = b_start
        state = k, w, b
        color = 'w'
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False
            self.draw(*state, color)
            ai_move = iterative_deepening_best_move(k, w, b, color)
            if ai_move is not None:
                try:
                    states.advance_state(k, w, b, *ai_move)
                except:
                    print("EXCEPTION, MOVE: ", ai_move)
                    return
                states.apply_captures(k, w, b, states.get_capture_victims(k, w, b, color, ai_move[1]))
                color = 'b' if color == 'w' else 'w'
            else:
                print("NULL MOVE DETECTED FOR PLAYER", color)
                self.isRunning = False
            pygame.time.delay(1000)

    def draw(self, k, w, b, current_turn, mouse_pos=None, move_origin=None, ):
        pygame.time.delay(10)
        grid_size = _WINDOW_SIZE // 9
        self.screen.fill((220, 220, 220))
        for row in range(9):
            for col in range(9):
                fill_color = 200, 200, 200
                if BUILDINGS[row, col]:
                    fill_color = (100, 100, 150)
                pygame.draw.rect(self.screen, fill_color, (
                    row * grid_size, col * grid_size, grid_size, grid_size
                ))
        if mouse_pos is not None:
            pygame.draw.rect(self.screen, (50, 50, 50), (
                (mouse_pos[0] // grid_size) * grid_size, (mouse_pos[1] // grid_size) * grid_size, grid_size, grid_size))
        if move_origin is not None:
            pygame.draw.rect(self.screen, (100, 150, 100), (
                move_origin[1] * grid_size, move_origin[0] * grid_size, grid_size, grid_size
            ))

        for j in range(0, _WINDOW_SIZE, _GRID_SIZE):
            pygame.draw.aaline(self.screen, (70, 73, 76), (j, 0), (j, _WINDOW_SIZE))
            pygame.draw.aaline(self.screen, (70, 73, 76), (0, j), (_WINDOW_SIZE, j))
        for row in range(9):
            for col in range(9):
                if b[row, col]:
                    fill_color = (30, 30, 30)
                elif w[row, col]:
                    fill_color = (240, 240, 240)
                elif k[row, col]:
                    fill_color = (240, 70, 70)
                else:
                    continue
                c_args = self.screen, col * grid_size + grid_size // 2, row * grid_size + grid_size // 2, int(
                    grid_size / 2.5)
                gfxdraw.filled_circle(*c_args, fill_color)
                gfxdraw.aacircle(*c_args, (50, 50, 50))
        curr_player = "Turn: White" if current_turn == 'w' else "Turn: Black"
        self.font.render_to(self.screen, (20, 20), curr_player, (20, 20, 20))
        pygame.display.update()
