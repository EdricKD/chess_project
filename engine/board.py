from .pieces import Pawn, Knight, Bishop, Rook, Queen, King

class Board():
    def __init__(self):
        self.board = self.create_board()
        self.wtomove = True
        self.mlog = []

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
            
    def print_board(self):
        for row in self.board:
            print(' '.join([piece.get_image_key().center(4) if piece else ' .  ' for piece in row]))

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7

    def get_piece(self, position: tuple[int, int]):
        row, col = position
        return self.board[row][col]
    


