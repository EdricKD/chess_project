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

        self.wtomove = True
        self.mlog = []
        return board
    
    def move(self, move):
        self.board[move.start_row][move.start_col] = None
        self.board[move.end_row][move.end_col] = move.pmove
        self.mlog.append(move)
        self.wtomove = not self.wtomove


    def undo(self):
        if len(self.mLog) != 0:
            last_move = self.mLog.pop()
            self.board[last_move.start_row][last_move.start_col] = last_move.pmove
            self.board[last_move.end_row][last_move.end_col] = last_move.pcapture
            
    def print_board(self):
        for row in self.board:
            print(' '.join([piece.center(3) if piece else ' . ' for piece in row]))
    


class Moves():

    # maps column index to file letter
    col_to_file = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
    # maps row index to rank number (row 0 is rank 8, row 7 is rank 1)
    row_to_rank = {0:'8', 1:'7', 2:'6', 3:'5', 4:'4', 5:'3', 6:'2', 7:'1'}


    def __init__(self, start_s, end_s, board):
        self.start_row = start_s[0]
        self.start_col = start_s[1]
        self.end_row = end_s[0]
        self.end_col = end_s[1]
        self.pmove = board[self.start_row][self.start_col]
        self.pcapture = board[self.end_row][self.end_col]
        self.notation = self.get_notation()

    def get_square(self, row, col):
        return self.col_to_file[col] + self.row_to_rank[row]

    def get_notation(self):
        piece = self.pmove[1:]   # strips colour prefix e.g. 'wKN' -> 'KN'
        capture = 'x' if self.pcapture else ''
        end_square = self.get_square(self.end_row, self.end_col)

        if piece == 'P':
            return capture + end_square        # e.g. 'e4' or 'xd5'
        elif piece == 'KN':
            return 'N' + capture + end_square  # e.g. 'Nf3' or 'Nxe5'
        else:
            return piece + capture + end_square # e.g. 'Be4', 'Qxd5'