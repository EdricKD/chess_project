import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame as py 

from engine import board
from engine import moves
from engine import pieces


WIDTH = HEIGHT = 512
DIMENSION = 8
S_SIZE = HEIGHT // DIMENSION
MAX_FPS = 20
IMAGES = {}


def images():
    pieces = ["bP", "bR", "bKN", "bB", "bQ", "bK", "wP", "wR", "wKN", "wB", "wQ", "wK"]
    for p in pieces:
        path = os.path.join(os.path.dirname(__file__), "Images", p + ".png")
        IMAGES[p] = py.transform.scale(py.image.load(path), (S_SIZE, S_SIZE))


PROMO_PIECES = [pieces.Queen, pieces.Rook, pieces.Bishop, pieces.Knight]
PROMO_KEYS = {'w': ['wQ', 'wR', 'wB', 'wKN'], 'b': ['bQ', 'bR', 'bB', 'bKN']}


def draw_promotion_panel(screen, color):
    panel_x = (WIDTH - 4 * S_SIZE) // 2
    panel_y = 0 if color == 'w' else HEIGHT - S_SIZE
    for i, key in enumerate(PROMO_KEYS[color]):
        x = panel_x + i * S_SIZE
        py.draw.rect(screen, py.Color("lightyellow"), py.Rect(x, panel_y, S_SIZE, S_SIZE))
        py.draw.rect(screen, py.Color("darkgray"), py.Rect(x, panel_y, S_SIZE, S_SIZE), 2)
        screen.blit(IMAGES[key], py.Rect(x, panel_y, S_SIZE, S_SIZE))


def get_promotion_choice(mouse_pos, color):
    panel_x = (WIDTH - 4 * S_SIZE) // 2
    panel_y = 0 if color == 'w' else HEIGHT - S_SIZE
    x, y = mouse_pos
    if panel_y <= y < panel_y + S_SIZE:
        idx = (x - panel_x) // S_SIZE
        if 0 <= idx < 4:
            return PROMO_PIECES[idx]
    return None


def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    clock = py.time.Clock()
    screen.fill(py.Color("white"))
    gs = board.Board()
    images()
    running = True
    pending_promotion = None
    s_selected =  () #Keep track of the last square selected
    p_clicks = [] #Keep track of player clicks
    while running:
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
            #mouse handler / presses
            elif e.type == py.MOUSEBUTTONDOWN:
                if pending_promotion is not None:
                    chosen = get_promotion_choice(py.mouse.get_pos(), pending_promotion[2])
                    if chosen is not None:
                        r, c, clr = pending_promotion
                        gs.board[r][c] = chosen(clr, (r, c))
                        pending_promotion = None
                else:
                    location = py.mouse.get_pos()
                    col = location[0] // S_SIZE
                    row = location[1] // S_SIZE
                    if not gs.wtomove:  # flip screen coords to board coords for black's turn
                        row, col = 7 - row, 7 - col
                    if s_selected == (row,col): #For if the user clicks the same square twice
                        s_selected = () #Deselects the square
                        p_clicks = []  #Clears the player clicks
                    else:
                        s_selected = (row, col)
                        p_clicks.append(s_selected)
                    if len(p_clicks) == 2:
                        piece = gs.board[p_clicks[0][0]][p_clicks[0][1]]

                        if piece is None:
                            s_selected = ()
                            p_clicks = []
                        elif (gs.wtomove and piece.color == 'w') or (not gs.wtomove and piece.color == 'b'):
                            valid_moves = gs.get_legal_moves(piece)
                            destination = p_clicks[1]

                            if destination in valid_moves:
                                move = moves.Moves(p_clicks[0], p_clicks[1], gs.board, gs.en_passant_target)
                                gs.move(move)
                                piece.moved = True
                                piece.position = destination

                                promo_row = 0 if piece.color == 'w' else 7
                                if isinstance(piece, pieces.Pawn) and destination[0] == promo_row:
                                    pending_promotion = (destination[0], destination[1], piece.color)

                            s_selected = ()
                            p_clicks = []

                        else:
                            s_selected = ()
                            p_clicks = []
            #key handlers (keyboard)
            elif e.type == py.KEYDOWN:
                if e.key == py.K_z:
                    gs.undo()


        VisualGameState(screen, gs, s_selected, not gs.wtomove)
        if pending_promotion is not None:
            draw_promotion_panel(screen, pending_promotion[2])
        clock.tick(MAX_FPS)
        py.display.flip()

def VisualGameState(screen, gs, s_selected, flipped):
    VisualBoard(screen)
    VisualHighlights(screen, gs, s_selected, flipped)  # after board, before pieces
    VisualPieces(screen, gs.board, flipped)

def b2s(r, c, flipped):
    """Convert board coordinates to screen coordinates."""
    if flipped:
        return 7 - r, 7 - c
    return r, c

def VisualHighlights(screen, gs, s_selected, flipped):
    # highlight king in check in red
    color = 'w' if gs.wtomove else 'b'
    if gs.is_in_check(color):
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = gs.board[r][c]
                if piece is not None and isinstance(piece, pieces.King) and piece.color == color:
                    sr, sc = b2s(r, c, flipped)
                    highlight = py.Surface((S_SIZE, S_SIZE))
                    highlight.set_alpha(180)
                    highlight.fill(py.Color("red"))
                    screen.blit(highlight, (sc * S_SIZE, sr * S_SIZE))

    if s_selected != ():
        row, col = s_selected
        piece = gs.board[row][col]

        # highlight selected square in green
        sr, sc = b2s(row, col, flipped)
        highlight = py.Surface((S_SIZE, S_SIZE))
        highlight.set_alpha(150)
        highlight.fill(py.Color("green"))
        screen.blit(highlight, (sc * S_SIZE, sr * S_SIZE))

        # highlight valid move squares
        if piece is not None and ((gs.wtomove and piece.color == 'w') or (not gs.wtomove and piece.color == 'b')):
            valid_moves = gs.get_legal_moves(piece)

            dot_surf = py.Surface((S_SIZE, S_SIZE), py.SRCALPHA)
            py.draw.circle(dot_surf, (0, 0, 0, 80), (S_SIZE // 2, S_SIZE // 2), S_SIZE // 6)

            cap_surf = py.Surface((S_SIZE, S_SIZE), py.SRCALPHA)
            cap_surf.fill((200, 0, 0, 100))

            for move_row, move_col in valid_moves:
                smr, smc = b2s(move_row, move_col, flipped)
                if gs.board[move_row][move_col] is None:
                    screen.blit(dot_surf, (smc * S_SIZE, smr * S_SIZE))
                else:
                    screen.blit(cap_surf, (smc * S_SIZE, smr * S_SIZE))


def VisualBoard(screen):
    colors = [py.Color("white"), py.Color("light blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            py.draw.rect(screen, color, py.Rect(c*S_SIZE, r*S_SIZE, S_SIZE, S_SIZE))

def VisualPieces(screen, board, flipped):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                key = piece.get_image_key()
                sr, sc = b2s(r, c, flipped)
                screen.blit(IMAGES[key], py.Rect(sc*S_SIZE, sr*S_SIZE, S_SIZE, S_SIZE))

if __name__ == "__main__":
    main()