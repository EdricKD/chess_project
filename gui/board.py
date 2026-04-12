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


def b2s(r, c, flipped):
    """Convert board coordinates to screen coordinates."""
    if flipped:
        return 7 - r, 7 - c
    return r, c


def main():
    py.init()
    screen = py.display.set_mode((WIDTH + PANEL_WIDTH, HEIGHT))
    clock = py.time.Clock()
    gs = board.Board()
    images()
    running = True
    pending_promotion = None
    s_selected = ()
    p_clicks = []
    menu_open = False
    button_rects = []
    selected_time = None
    time_options = {"3 min": 180, "5 min": 300, "10 min": 600, "Unlimited": None}
    pending_resign = None
    white_time = None
    black_time = None
    last_tick = None
    game_over = None  # None, or a result string e.g. "White wins by checkmate!"

    while running:
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False

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
                                white_time = selected_time
                                black_time = selected_time
                                last_tick = py.time.get_ticks() if selected_time else None
                                s_selected = ()
                                p_clicks = []
                                pending_promotion = None
                                game_over = None
                            elif label == "Freestyle":
                                gs = board.Board(freestyle=True, score=gs.score)
                                white_time = selected_time
                                black_time = selected_time
                                last_tick = py.time.get_ticks() if selected_time else None
                                s_selected = ()
                                p_clicks = []
                                game_over = None
                            elif label in time_options:
                                selected_time = time_options[label]
                            elif label == "Resign White":
                                pending_resign = 'w'
                            elif label == "Resign Black":
                                pending_resign = 'b'
                            elif label == "Confirm Resign" and pending_resign:
                                gs.score['b' if pending_resign == 'w' else 'w'] += 1
                                gs = board.Board(score=gs.score)
                                white_time = selected_time
                                black_time = selected_time
                                last_tick = py.time.get_ticks() if selected_time else None
                                s_selected = ()
                                p_clicks = []
                                pending_promotion = None
                                pending_resign = None
                                game_over = None
                                menu_open = False
                            elif label == "Cancel":
                                pending_resign = None

                # Only handle board clicks when no promotion pending, menu closed, and game not over
                elif not menu_open and game_over is None:
                    if not gs.wtomove:  # flip screen coords to board coords for black's turn
                        row, col = 7 - row, 7 - col
                    if s_selected == (row, col):
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
                                if last_tick is not None:
                                    last_tick = py.time.get_ticks()

                                promo_row = 0 if piece.color == 'w' else 7
                                if isinstance(piece, pieces.Pawn) and destination[0] == promo_row:
                                    pending_promotion = (destination[0], destination[1], piece.color)

                                # Check for game end after the move
                                current = 'w' if gs.wtomove else 'b'
                                opponent_name = 'Black' if current == 'w' else 'White'
                                if gs.is_checkmate(current):
                                    game_over = f"{opponent_name} wins by checkmate!"
                                    gs.score['b' if current == 'w' else 'w'] += 1
                                elif gs.is_stalemate(current):
                                    game_over = "Stalemate — draw!"
                                    gs.score['draws'] += 1

                            s_selected = ()
                            p_clicks = []
                        else:
                            s_selected = ()
                            p_clicks = []

            elif e.type == py.KEYDOWN:
                if e.key == py.K_z:
                    gs.undo()
                elif e.key == py.K_ESCAPE:
                    menu_open = not menu_open

        # tick clock every frame, outside event loop
        if last_tick is not None and white_time is not None:
            now = py.time.get_ticks()
            elapsed = (now - last_tick) / 1000
            last_tick = now

            if gs.wtomove:
                white_time = max(0, white_time - elapsed)
                if white_time == 0:
                    gs.score['b'] += 1
                    game_over = "Black wins on time!"
            else:
                black_time = max(0, black_time - elapsed)
                if black_time == 0:
                    gs.score['w'] += 1
                    game_over = "White wins on time!"

        flipped = not gs.wtomove
        VisualGameState(screen, gs, s_selected, flipped)
        if pending_promotion is not None:
            draw_promotion_panel(screen, pending_promotion[2])
        if game_over is not None:
            draw_game_over(screen, game_over)
        button_rects = draw_panel(screen, gs, menu_open, selected_time, pending_resign, white_time, black_time)
        clock.tick(MAX_FPS)
        py.display.flip()


def VisualGameState(screen, gs, s_selected, flipped):
    VisualBoard(screen)
    VisualHighlights(screen, gs, s_selected, flipped)
    VisualPieces(screen, gs.board, flipped)


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
            color = colors[((r + c) % 2)]
            py.draw.rect(screen, color, py.Rect(c * S_SIZE, r * S_SIZE, S_SIZE, S_SIZE))


def VisualPieces(screen, board, flipped):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                key = piece.get_image_key()
                sr, sc = b2s(r, c, flipped)
                screen.blit(IMAGES[key], py.Rect(sc * S_SIZE, sr * S_SIZE, S_SIZE, S_SIZE))


def draw_game_over(screen, message):
    overlay = py.Surface((WIDTH, HEIGHT), py.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    font = py.font.SysFont("monospace", 22, bold=True)
    text = font.render(message, True, py.Color("white"))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))

    bg = py.Rect(text_rect.left - 16, text_rect.top - 12, text_rect.width + 32, text_rect.height + 24)
    py.draw.rect(screen, py.Color("gray20"), bg, border_radius=8)
    py.draw.rect(screen, py.Color("gray60"), bg, 2, border_radius=8)
    screen.blit(text, text_rect)

    small = py.font.SysFont("monospace", 13)
    hint = small.render("New Game from menu  |  Z to undo", True, py.Color("gray70"))
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))


def draw_panel(screen, gs, menu_open, selected_time, pending_resign, white_time, black_time):
    panel_rect = py.Rect(WIDTH, 0, PANEL_WIDTH, HEIGHT)
    py.draw.rect(screen, py.Color("gray20"), panel_rect)
    button_rects = []

    def format_time(seconds):
        if seconds is None:
            return "--:--"
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02}:{secs:02}"

    # always draw clocks at bottom regardless of menu state
    clock_font = py.font.SysFont("monospace", 16)
    w_color = py.Color("white") if gs.wtomove else py.Color("gray50")
    b_color = py.Color("white") if not gs.wtomove else py.Color("gray50")
    screen.blit(clock_font.render(f"W: {format_time(white_time)}", True, w_color), (WIDTH + 20, HEIGHT - 60))
    screen.blit(clock_font.render(f"B: {format_time(black_time)}", True, b_color), (WIDTH + 20, HEIGHT - 35))

    if not menu_open:
        font = py.font.SysFont("monospace", 12)
        screen.blit(font.render("ESC = menu", True, py.Color("gray60")), (WIDTH + 10, HEIGHT - 80))
        return button_rects

    font = py.font.SysFont("monospace", 15)
    screen.blit(font.render("MENU", True, py.Color("white")), (WIDTH + 70, 20))

    small = py.font.SysFont("monospace", 12)
    screen.blit(small.render(f"W: {gs.score['w']}  B: {gs.score['b']}  D: {gs.score['draws']}",
                True, py.Color("gray70")), (WIDTH + 15, 35))

    if pending_resign:
        msg_font = py.font.SysFont("monospace", 13)
        color_name = "White" if pending_resign == 'w' else "Black"
        screen.blit(msg_font.render(f"{color_name} resigns?", True, py.Color("white")), (WIDTH + 20, HEIGHT // 2 - 40))
        for i, label in enumerate(["Confirm Resign", "Cancel"]):
            rect = py.Rect(WIDTH + 20, HEIGHT // 2 + i * 55, 160, 40)
            color = py.Color("firebrick") if label == "Confirm Resign" else py.Color("gray40")
            py.draw.rect(screen, color, rect, border_radius=6)
            screen.blit(font.render(label, True, py.Color("white")), (rect.x + 10, rect.y + 10))
            button_rects.append((label, rect))
        return button_rects

    time_options = {"3 min": 180, "5 min": 300, "10 min": 600, "Unlimited": None}
    buttons = ["New Game", "Freestyle", "3 min", "5 min", "10 min", "Unlimited", "Resign White", "Resign Black"]

    for i, label in enumerate(buttons):
        rect = py.Rect(WIDTH + 20, 60 + i * 55, 160, 40)
        is_active = (label in time_options and time_options[label] == selected_time)
        color = py.Color("steelblue") if is_active else py.Color("gray40")
        py.draw.rect(screen, color, rect, border_radius=6)
        screen.blit(font.render(label, True, py.Color("white")), (rect.x + 10, rect.y + 10))
        button_rects.append((label, rect))

    return button_rects


if __name__ == "__main__":
    main()
