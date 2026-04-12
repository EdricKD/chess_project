from .pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board():
    def __init__(self):
        self.board = self.create_board()
        self.wtomove = True
        self.mlog = []
        self.en_passant_target = None  # square a pawn can capture to via en passant
        self.score = {'w': 0, 'b': 0, 'draws': 0} #Keeps track of each color's win rate

    def create_board(self):
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

    def move(self, move):
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
        if len(self.mlog) != 0:
            last_move = self.mlog.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.pmove
            self.board[last_move.end_row][last_move.end_col] = last_move.pcapture
            self.en_passant_target = last_move.prev_en_passant_target
            self.wtomove = not self.wtomove

            # restore piece state
            last_move.pmove.position = (last_move.start_row, last_move.start_col)
            last_move.pmove.moved = False
            
    def print_board(self):
        for row in self.board:
            print(' '.join([piece.get_image_key().center(4) if piece else ' .  ' for piece in row]))

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7

    def get_piece(self, position: tuple[int, int]):
        row, col = position
        return self.board[row][col]

    def is_square_attacked(self, square, attacker_color) -> bool:
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and piece.color == attacker_color:
                    if square in piece.get_attacks(self):
                        return True
        return False

    def is_in_check(self, color) -> bool:
        opponent = 'b' if color == 'w' else 'w'
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece is not None and isinstance(piece, King) and piece.color == color:
                    return self.is_square_attacked((r, c), opponent)
        return False

    def get_legal_moves(self, piece) -> list[tuple[int, int]]:
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

    def _leaves_king_in_check(self, piece, end) -> bool:
        """Simulates moving piece to end, checks if own king is in check, then undoes."""
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
    
    #This class is for a special type of chess called freestyle chess
    #It allows for the creation of a randomised back rank
    def __init__(self, freestyle=False, score=None):
        self.board = self.create_freestyle_board() if freestyle else self.create_board()
        self.wtomove = True
        self.mlog = []
        self.en_passant_target = None
        self.score = score if score else {'w': 0, 'b': 0, 'draws': 0}
    
    #This is the freestyle method itself
    def create_freestyle_board(self):
        import random
        board = [[None]*8 for _ in range(8)]

        # pawns stay exactly where they are
        for col in range(8):
            board[1][col] = Pawn('b', (1, col))
            board[6][col] = Pawn('w', (6, col))

        # shuffle back rank pieces for both colors
        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        
        # white back rank
        white_back = back_row.copy()
        random.shuffle(white_back)
        for col, PieceClass in enumerate(white_back):
            board[7][col] = PieceClass('w', (7, col))

        # black back rank
        black_back = back_row.copy()
        random.shuffle(black_back)
        for col, PieceClass in enumerate(black_back):
            board[0][col] = PieceClass('b', (0, col))

        return board

