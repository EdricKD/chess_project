class Board():
    def __init__(self):
        self.board = self.create_board()
        self.wtomove = True
        self.mlog = []

    def create_board(self):
        board = [
            ['bR', 'bKN', 'bB', 'bQ', 'bK', 'bB', 'bKN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wKN', 'wB', 'wQ', 'wK', 'wB', 'wKN', 'wR']   
        ]

        
        return board
    
    def move(self, move):
        self.board[move.start_row][move.start_col] = None
        self.board[move.end_row][move.end_col] = move.pmove
        self.mlog.append(move)
        self.wtomove = not self.wtomove


    def undo(self):
        if len(self.mlog) != 0:
            last_move = self.mlog.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.pmove
            self.board[last_move.end_row][last_move.end_col] = last_move.pcapture
            
    def print_board(self):
        for row in self.board:
            print(' '.join([piece.center(3) if piece else ' . ' for piece in row]))

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7

    def get_piece(self, position: tuple[int, int]):
        row, col = position
        return self.board[row][col]
    


