from .pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board():
    def __init__(self, freestyle=False, score=None):
        """Initialise a new game. Set freestyle=True for randomised back ranks.
        Pass an existing score dict to carry scores across games."""
        self.board = self.create_freestyle_board() if freestyle else self.create_board()
        self.wtomove = True
        self.mlog = []
        self.en_passant_target = None
        self.score = score if score else {'w': 0, 'b': 0, 'draws': 0}

    def create_board(self):
        """Return an 8x8 list representing the standard starting position."""
        board = [[None]*8 for _ in range(8)]

        for col in range(8):
            board[1][col] = Pawn('b', (1, col))
            board[6][col] = Pawn('w', (6, col))

        # Place back row pieces
        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, PieceClass in enumerate(back_row):
            board[0][col] = PieceClass('b', (0, col))
            board[7][col] = PieceClass('w', (7, col))

        return board

    def create_freestyle_board(self):
        """Return an 8x8 list with pawns in standard positions but both
        back ranks randomly shuffled (Fischer Random / Chess960 style)."""
        import random
        board = [[None]*8 for _ in range(8)]

        # Pawns stay exactly where they are
        for col in range(8):
            board[1][col] = Pawn('b', (1, col))
            board[6][col] = Pawn('w', (6, col))

        # Shuffle back rank pieces independently for each color
        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        white_back = back_row.copy()
        random.shuffle(white_back)
        for col, PieceClass in enumerate(white_back):
            board[7][col] = PieceClass('w', (7, col))

        black_back = back_row.copy()
        random.shuffle(black_back)
        for col, PieceClass in enumerate(black_back):
            board[0][col] = PieceClass('b', (0, col))

        return board

    def move(self, move):
        """Apply a Move to the board: update piece positions, switch turn,
        handle en passant target setting/capture, and move castling rooks."""
        self.board[move.start_row][move.start_col] = None
        self.board[move.end_row][move.end_col] = move.pmove
        self.mlog.append(move)
        self.wtomove = not self.wtomove

        # Update en passant target
        self.en_passant_target = None
        if isinstance(move.pmove, Pawn):
            if abs(move.end_row - move.start_row) == 2:
                # Double pawn push: set EP target to the skipped square
                direction = -1 if move.pmove.color == 'w' else 1
                self.en_passant_target = (move.start_row + direction, move.start_col)
            elif move.end_col != move.start_col and move.pcapture is None:
                # Diagonal move to empty square = en passant capture
                direction = -1 if move.pmove.color == 'w' else 1
                ep_row = move.end_row - direction  # row the captured pawn is on
                move.ep_captured_piece = self.board[ep_row][move.end_col]
                move.ep_captured_pos = (ep_row, move.end_col)
                self.board[ep_row][move.end_col] = None

        if isinstance(move.pmove, King):
            # Kingside
            if move.end_col - move.start_col == 2:
                rook = self.board[move.end_row][7]
                self.board[move.end_row][5] = rook
                self.board[move.end_row][7] = None
                rook.position = (move.end_row, 5)
                rook.moved = True
            # Queenside
            elif move.end_col - move.start_col == -2:
                rook = self.board[move.end_row][0]
                self.board[move.end_row][3] = rook
                self.board[move.end_row][0] = None
                rook.position = (move.end_row, 3)
                rook.moved = True

    def undo(self):
        """Revert the last move: restore pieces, en passant state, turn,
        and undo castling rook movement and en passant captures."""
        if len(self.mlog) != 0:
            last_move = self.mlog.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.pmove
            self.board[last_move.end_row][last_move.end_col] = last_move.pcapture
            self.en_passant_target = last_move.prev_en_passant_target
            self.wtomove = not self.wtomove

            # Restore piece position
            last_move.pmove.position = (last_move.start_row, last_move.start_col)
            last_move.pmove.moved = False

            # Restore en passant captured pawn
            if last_move.ep_captured_pos is not None:
                r, c = last_move.ep_captured_pos
                self.board[r][c] = last_move.ep_captured_piece
                last_move.ep_captured_piece.position = (r, c)

            # Restore castling rook
            if isinstance(last_move.pmove, King):
                col_diff = last_move.end_col - last_move.start_col
                row = last_move.start_row
                if col_diff == 2:  # kingside: rook moved from col 7 to col 5
                    rook = self.board[row][5]
                    self.board[row][7] = rook
                    self.board[row][5] = None
                    rook.position = (row, 7)
                    rook.moved = False
                elif col_diff == -2:  # queenside: rook moved from col 0 to col 3
                    rook = self.board[row][3]
                    self.board[row][0] = rook
                    self.board[row][3] = None
                    rook.position = (row, 0)
                    rook.moved = False

    def print_board(self):
        """Print a text representation of the board to stdout (debug helper)."""
        for row in self.board:
            print(' '.join([piece.get_image_key().center(4) if piece else ' .  ' for piece in row]))

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        """Return True if (row, col) is within the 8x8 board."""
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7

    def get_piece(self, position: tuple[int, int]):
        """Return the piece at (row, col), or None if the square is empty."""
        row, col = position
        return self.board[row][col]

    def is_square_attacked(self, square, attacker_color) -> bool:
        """Return True if any piece of attacker_color can attack the given square."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == attacker_color:
                    if square in piece.get_attacks(self):
                        return True
        return False

    def is_in_check(self, color) -> bool:
        """Return True if the king of the given color is currently in check."""
        opponent = 'b' if color == 'w' else 'w'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and isinstance(piece, King) and piece.color == color:
                    return self.is_square_attacked((r, c), opponent)
        return False

    def get_legal_moves(self, piece) -> list[tuple[int, int]]:
        """Return all fully legal destination squares for piece.
        Filters pseudo-legal moves by simulating each and checking for self-check.
        Also enforces castling rules (can't castle through or out of check)."""
        pseudo_moves = piece.get_valid_moves(self)
        legal = []
        opponent = 'b' if piece.color == 'w' else 'w'

        for end in pseudo_moves:
            if isinstance(piece, King):
                col_diff = end[1] - piece.position[1]
                if abs(col_diff) == 2:  # castling move
                    if self.is_square_attacked(piece.position, opponent):
                        continue  # can't castle while in check
                    mid_col = piece.position[1] + (1 if col_diff > 0 else -1)
                    if self.is_square_attacked((piece.position[0], mid_col), opponent):
                        continue  # can't castle through check

            if not self._leaves_king_in_check(piece, end):
                legal.append(end)
        return legal

    def has_any_legal_moves(self, color) -> bool:
        """Return True if the given color has at least one legal move available."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == color:
                    if len(self.get_legal_moves(piece)) > 0:
                        return True
        return False

    def is_checkmate(self, color) -> bool:
        """Return True if the given color is in checkmate (in check with no legal moves)."""
        return self.is_in_check(color) and not self.has_any_legal_moves(color)

    def is_stalemate(self, color) -> bool:
        """Return True if the given color is in stalemate (not in check, but no legal moves)."""
        return not self.is_in_check(color) and not self.has_any_legal_moves(color)

    def _leaves_king_in_check(self, piece, end) -> bool:
        """Simulate moving piece to end, check if own king ends up in check, then undo.
        Also handles the en passant edge case where a second pawn is removed."""
        start = piece.position
        captured = self.board[end[0]][end[1]]

        # If this is an en passant capture, also temporarily remove the captured pawn
        ep_square = None
        ep_piece = None
        if (isinstance(piece, Pawn) and end == self.en_passant_target
                and end[1] != start[1] and captured is None):
            direction = -1 if piece.color == 'w' else 1
            ep_square = (end[0] - direction, end[1])
            ep_piece = self.board[ep_square[0]][ep_square[1]]
            self.board[ep_square[0]][ep_square[1]] = None

        self.board[start[0]][start[1]] = None
        self.board[end[0]][end[1]] = piece
        piece.position = end

        in_check = self.is_in_check(piece.color)

        self.board[start[0]][start[1]] = piece
        self.board[end[0]][end[1]] = captured
        piece.position = start
        if ep_square is not None:
            self.board[ep_square[0]][ep_square[1]] = ep_piece
        return in_check
