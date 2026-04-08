"""
File for all piece logic and classes. Each piece will be a subclass of the Piece class, and will have its own move logic.
"""
from .board import Board

#Major class 'Piece' for features all pieces on the board have
class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.color = color
        self.position = position
        self.moved = False

    def has_moved(self):
        pass

    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        pass

#All featues for the PAWN piece
class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        moves = []
        direction = 1 if self.color == 'w' else -1

        one_ahead = (row + direction, col)
        if board.is_in_bounds(one_ahead) and board.get_piece(one_ahead) is None:
           moves.append(one_ahead) 

           two_ahead = (row + direction*2, col)
           if not self.moved and board.is_in_bounds(two_ahead) and board.get_piece(two_ahead) is None:
               moves.append(two_ahead)
            
        for diagonal_capture in [-1,1]:
            capture_square = (row + direction, col + diagonal_capture)
            if board.is_in_bounds(capture_square):
                target = board.get_piece(capture_square)
                if target is not None and target.color != self.color:
                        moves.append(capture_square)
        
        return moves

#All features for the KNIGHT piece
class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(-2,-1), (-2, 1), (2, 1), (2, -1)
                   (-1,-2), (-1,2), (1,2), (1,-2)]
        
        for direction_row, direction_column in offsets:
            destination = (row + direction_row, col + direction_column)
            if board.is_in_bounds(destination):
                target = board.get_piece(destination)
                if target is None or target.color != self.color:
                    moves.append(target)

        return moves
    
#All features for the BISHOP piece
class Bishop(Piece):
    def __init__(self,color,position):
        super().__init__(color,position)
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,1), (1,-1), (-1,1), (-1,-1)]

        for direction_row, direction_column in offsets:
            destination = (row + direction_row, col + direction_column)
            if board.is_in_bounds(destination):
                target = board.get_piece(destination)
                if target is None or target.color != self.color:
                    moves.append(destination)
        return moves


#All features for the ROOK piece
class Rook(Piece):
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        pass

#All features for the QUEEN piece
class Queen(Piece):
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        pass

#All features for the KING piece, including special conditions 
class King(Piece):
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        pass