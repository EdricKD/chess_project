class Board():
    def __init__(self):
        self.board = self.create_board()

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
    
    def print_board(self):
        for row in self.board:
            print(' '.join([str(piece) if piece else '  ' for piece in row]))