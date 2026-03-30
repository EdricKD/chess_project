"""
File for all piece logic and classes. Each piece will be a subclass of the Piece class, and will have its own move logic.
"""
from .board import Board

#Major class 'Piece' for features all pieces on the board have
class Piece:
    def __init__(self, color: str, position: tuple[int, int]):
        self.color = color
        self.position = position

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
        pass

#All features for the KNIGHT piece
class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        moves = []
        pass

#All features for the BISHOP piece
class Bishop(Piece):
    def get_valid_moves(self, board: Board) -> list[tuple[int, int]]:
        pass

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