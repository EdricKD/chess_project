class Moves():
    """Represents a single move: stores start/end squares, the moving piece,
    any captured piece, en passant state, and algebraic notation."""

    # Maps column index to file letter (a–h)
    col_to_file = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
    # Maps row index to rank number (row 0 = rank 8, row 7 = rank 1)
    row_to_rank = {0:'8', 1:'7', 2:'6', 3:'5', 4:'4', 5:'3', 6:'2', 7:'1'}

    def __init__(self, start_s, end_s, board, en_passant_target=None):
        """Capture a snapshot of the move at creation time.
        en_passant_target is the current board EP square, saved for undo."""
        self.start_row = start_s[0]
        self.start_col = start_s[1]
        self.end_row = end_s[0]
        self.end_col = end_s[1]
        self.pmove = board[self.start_row][self.start_col]       # piece being moved
        self.pcapture = board[self.end_row][self.end_col]         # piece being captured (or None)
        self.prev_en_passant_target = en_passant_target           # for undo
        self.ep_captured_piece = None   # set by Board.move() if this was an EP capture
        self.ep_captured_pos = None
        self.notation = self.get_notation()

    def get_square(self, row, col):
        """Convert (row, col) indices to algebraic square notation, e.g. (6,4) -> 'e2'."""
        return self.col_to_file[col] + self.row_to_rank[row]

    def get_notation(self):
        """Build standard algebraic notation for this move (e.g. 'e4', 'Nxf3', 'Rxe1')."""
        from .pieces import Pawn, Knight, Bishop, Rook, Queen, King

        piece_map = {Pawn: 'P', Knight: 'KN', Bishop: 'B',
                     Rook: 'R', Queen: 'Q', King: 'K'}

        piece = piece_map[type(self.pmove)]
        capture = 'x' if self.pcapture else ''
        end_square = self.get_square(self.end_row, self.end_col)

        if piece == 'P':
            if self.pcapture:
                return self.col_to_file[self.start_col] + 'x' + end_square
            else:
                return end_square
        elif piece == 'KN':
            return 'N' + capture + end_square
        else:
            return piece + capture + end_square
