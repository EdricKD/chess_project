"""
File for all piece logic and classes. Each piece will be a subclass of the Piece class, and will have its own move logic.
"""
#Major class 'Piece' for features all pieces on the board have
class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.color = color
        self.position = position
        self.moved = False

    def has_moved(self):
        pass

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        pass

    def get_image_key(self):
        piece_map = {
            Pawn: 'P', Knight: 'KN', Bishop: 'B',
            Rook: 'R', Queen: 'Q', King: 'K'
        }
        return self.color + piece_map[type(self)]

#All featues for the PAWN piece
class Pawn(Piece):
    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position
        direction = -1 if self.color == 'w' else 1  # fixed

        one_ahead = (row + direction, col)
        if board.is_in_bounds(one_ahead) and board.get_piece(one_ahead) is None:
            moves.append(one_ahead)

            two_ahead = (row + direction*2, col)
            if not self.moved and board.is_in_bounds(two_ahead) and board.get_piece(two_ahead) is None:
                moves.append(two_ahead)

        for dc in [-1, 1]:
            capture_square = (row + direction, col + dc)
            if board.is_in_bounds(capture_square):
                target = board.get_piece(capture_square)
                if target is not None and target.color != self.color:
                    moves.append(capture_square)

        return moves
    
#All features for the KNIGHT piece
class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(-2,-1), (-2, 1), (2, 1), (2, -1),
                   (-1,-2), (-1,2), (1,2), (1,-2)]
        
        for direction_row, direction_column in offsets:
            destination = (row + direction_row, col + direction_column)
            if board.is_in_bounds(destination):
                target = board.get_piece(destination)
                if target is None or target.color != self.color:
                    moves.append(destination)

        return moves
    
#All features for the BISHOP piece
class Bishop(Piece):
    def __init__(self,color,position):
        super().__init__(color,position)
    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,1), (1,-1), (-1,1), (-1,-1)]

        for direction_row, direction_column in offsets:
            r, c = row + direction_row, col + direction_column
            while board.is_in_bounds((r,c)):
                target = board.get_piece((r,c))
                if target is None:
                    moves.append((r,c))
                elif target.color != self.color:
                    moves.append((r,c))
                    break
                else:
                    break
                r += direction_row
                c += direction_column
        return moves


#All features for the ROOK piece
class Rook(Piece):
    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,0), (-1,0), (0,1), (0,-1)]

        for direction_row, direction_column in offsets:
            r, c = row + direction_row, col + direction_column
            while board.is_in_bounds((r,c)):
                target = board.get_piece((r,c))
                if target is None:
                    moves.append((r,c))
                elif target.color != self.color:
                    moves.append((r,c))
                    break
                else:
                    break
                r += direction_row
                c += direction_column
        return moves
        

#All features for the QUEEN piece
class Queen(Piece):
    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]

        for direction_row, direction_column in offsets:
            r, c = row + direction_row, col + direction_column
            while board.is_in_bounds((r,c)):
                target = board.get_piece((r,c))
                if target is None:
                    moves.append((r,c))
                elif target.color != self.color:
                    moves.append((r,c))
                    break
                else:
                    break
                r += direction_row
                c += direction_column
        
        return moves

#All features for the KING piece, including special conditions 
class King(Piece):
    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        for direction_row, direction_column in offsets:
            destination = (row + direction_row, col + direction_column)
            if board.is_in_bounds(destination):
                target = board.get_piece(destination)
                if target is None or target.color != self.color:
                    moves.append(destination) 