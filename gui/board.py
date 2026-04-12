import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame as py

from engine import board
from engine import moves
from engine import pieces


WIDTH = HEIGHT = 512
DIMENSION = 8
PANEL_WIDTH = 200
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
    screen = py.display.set_mode((WIDTH + PANEL_WIDTH, HEIGHT))
    clock = py.time.Clock()
    screen.fill(py.Color("white"))
    gs = board.Board()
    images()
    running = True
    pending_promotion = None
    s_selected = ()  # Keep track of the last square selected
    p_clicks = []    # Keep track of player clicks
    menu_open = False
    button_rects = []
    selected_time = None
    time_options = {"3 min": 180, "5 min": 300, "10 min": 600, "Unlimited": None}
    pending_resign = None

    while running:
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
            # mouse handler / presses
            elif e.type == py.MOUSEBUTTONDOWN:
                location = py.mouse.get_pos()
                col = location[0] // S_SIZE
                row = location[1] // S_SIZE

                if pending_promotion is not None:
                    # Promotion choice takes priority over everything else
                    chosen = get_promotion_choice(location, pending_promotion[2])
                    if chosen is not None:
                        r, c, clr = pending_promotion
                        gs.board[r][c] = chosen(clr, (r, c))
                        pending_promotion = None

                elif menu_open and button_rects:
                    for label, rect in button_rects:
                        if rect.collidepoint(location):
                            if label == "New Game":
                                gs = board.Board(score=gs.score)
                                s_selected = ()
                                p_clicks = []
                                pending_promotion = None
                            elif label == "Freestyle":
                                gs = board.Board(freestyle=True, score=gs.score)
                                s_selected = ()
                                p_clicks = []
                            elif label in time_options:
                                selected_time = time_options[label]
                            elif label == "Resign White":
                                pending_resign = 'w'
                            elif label == "Resign Black":
                                pending_resign = 'b'
                            elif label == "Confirm Resign" and pending_resign:
                                gs.score['b' if pending_resign == 'w' else 'w'] += 1
                                gs = board.Board(score=gs.score)
                                s_selected = ()
                                p_clicks = []
                                pending_promotion = None
                                pending_resign = None
                                menu_open = False
                            elif label == "Cancel":
                                pending_resign = None

                # Only handle board clicks when no promotion pending and menu is closed
                elif not menu_open:
                    if not gs.wtomove:  # flip screen coords to board coords for black's turn
                        row, col = 7 - row, 7 - col
                    if s_selected == (row, col):  # clicked same square twice — deselect
                        s_selected = ()
                        p_clicks = []
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

            # key handlers (keyboard)
            elif e.type == py.KEYDOWN:
                if e.key == py.K_z:
                    gs.undo()
                elif e.key == py.K_ESCAPE:
                    menu_open = not menu_open

        VisualGameState(screen, gs, s_selected, not gs.wtomove)
        if pending_promotion is not None:
            draw_promotion_panel(screen, pending_promotion[2])
        button_rects = draw_panel(screen, gs, menu_open, selected_time, pending_resign)
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

def draw_panel(screen, gs, menu_open, selected_time, pending_resign):
    panel_rect = py.Rect(WIDTH, 0, PANEL_WIDTH, HEIGHT)
    py.draw.rect(screen, py.Color("gray20"), panel_rect)
    button_rects = []

    if not menu_open:
        font = py.font.SysFont("monospace", 12)
        hint = font.render("ESC = menu", True, py.Color("gray60"))
        screen.blit(hint, (WIDTH + 10, HEIGHT - 20))
        return button_rects

    font = py.font.SysFont("monospace", 15)
    title = font.render("MENU", True, py.Color("white"))
    screen.blit(title, (WIDTH + 70, 20))

    small = py.font.SysFont("monospace", 12)
    screen.blit(small.render(f"W: {gs.score['w']}  B: {gs.score['b']}  D: {gs.score['draws']}",
                True, py.Color("gray70")), (WIDTH + 15, 35))

    if pending_resign:
        msg_font = py.font.SysFont("monospace", 13)
        color_name = "White" if pending_resign == 'w' else "Black"
        msg = msg_font.render(f"{color_name} resigns?", True, py.Color("white"))
        screen.blit(msg, (WIDTH + 20, HEIGHT // 2 - 40))

        for i, label in enumerate(["Confirm Resign", "Cancel"]):
            rect = py.Rect(WIDTH + 20, HEIGHT // 2 + i * 55, 160, 40)
            color = py.Color("firebrick") if label == "Confirm Resign" else py.Color("gray40")
            py.draw.rect(screen, color, rect, border_radius=6)
            text = font.render(label, True, py.Color("white"))
            screen.blit(text, (rect.x + 10, rect.y + 10))
            button_rects.append((label, rect))

        return button_rects

    # normal buttons
    time_options = {"3 min": 180, "5 min": 300, "10 min": 600, "Unlimited": None}
    buttons = ["New Game", "Freestyle", "3 min", "5 min", "10 min", "Unlimited", "Resign White", "Resign Black"]

    for i, label in enumerate(buttons):
        rect = py.Rect(WIDTH + 20, 60 + i * 55, 160, 40)
        is_active = (label in time_options and time_options[label] == selected_time)
        color = py.Color("steelblue") if is_active else py.Color("gray40")
        py.draw.rect(screen, color, rect, border_radius=6)
        text = font.render(label, True, py.Color("white"))
        screen.blit(text, (rect.x + 10, rect.y + 10))
        button_rects.append((label, rect))

    return button_rects

if __name__ == "__main__":
    main()
