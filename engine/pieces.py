"""
Piece classes for the chess engine.
Each piece subclasses Piece and implements get_valid_moves() for movement rules.
Pieces that attack differently from how they move also override get_attacks().
"""

class Piece:
    """Base class for all chess pieces."""

    def __init__(self, color: str, position: tuple[int, int]):
        """color: 'w' or 'b'. position: (row, col) on the board."""
        self.color = color
        self.position = position
        self.moved = False  # used for pawn double-push and castling eligibility

    def has_moved(self):
        pass

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        """Return pseudo-legal destination squares (no check filtering)."""
        pass

    def get_attacks(self, board) -> list[tuple[int, int]]:
        """Return squares this piece attacks, used for check detection.
        Defaults to get_valid_moves; overridden where attack pattern differs (Pawn, King)."""
        return self.get_valid_moves(board)

    def get_image_key(self):
        """Return the image dictionary key for this piece, e.g. 'wP' or 'bKN'."""
        piece_map = {
            Pawn: 'P', Knight: 'KN', Bishop: 'B',
            Rook: 'R', Queen: 'Q', King: 'K'
        }
        return self.color + piece_map[type(self)]


class Pawn(Piece):
    """Pawn: moves forward one square, two on first move, captures diagonally.
    Supports en passant capture via board.en_passant_target."""

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position
        direction = -1 if self.color == 'w' else 1

        # Forward one square
        one_ahead = (row + direction, col)
        if board.is_in_bounds(one_ahead) and board.get_piece(one_ahead) is None:
            moves.append(one_ahead)

            # Forward two squares from starting rank
            two_ahead = (row + direction*2, col)
            if not self.moved and board.is_in_bounds(two_ahead) and board.get_piece(two_ahead) is None:
                moves.append(two_ahead)

        # Diagonal captures
        for dc in [-1, 1]:
            capture_square = (row + direction, col + dc)
            if board.is_in_bounds(capture_square):
                target = board.get_piece(capture_square)
                if target is not None and target.color != self.color:
                    moves.append(capture_square)

        # En passant
        if board.en_passant_target is not None:
            ep_row, ep_col = board.en_passant_target
            if ep_row == row + direction and abs(ep_col - col) == 1:
                moves.append(board.en_passant_target)

        return moves

    def get_attacks(self, board) -> list[tuple[int, int]]:
        """Pawns attack diagonally only, regardless of whether a piece is there."""
        attacks = []
        row, col = self.position
        direction = -1 if self.color == 'w' else 1
        for dc in [-1, 1]:
            sq = (row + direction, col + dc)
            if board.is_in_bounds(sq):
                attacks.append(sq)
        return attacks


class Knight(Piece):
    """Knight: moves in an L-shape, jumps over other pieces."""

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


class Bishop(Piece):
    """Bishop: slides diagonally any number of squares."""

    def __init__(self, color, position):
        super().__init__(color, position)

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,1), (1,-1), (-1,1), (-1,-1)]

        for direction_row, direction_column in offsets:
            r, c = row + direction_row, col + direction_column
            while board.is_in_bounds((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += direction_row
                c += direction_column
        return moves


class Rook(Piece):
    """Rook: slides horizontally or vertically any number of squares."""

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,0), (-1,0), (0,1), (0,-1)]

        for direction_row, direction_column in offsets:
            r, c = row + direction_row, col + direction_column
            while board.is_in_bounds((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += direction_row
                c += direction_column
        return moves


class Queen(Piece):
    """Queen: combines rook and bishop movement (slides in all 8 directions)."""

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        moves = []
        row, col = self.position

        offsets = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]

        for direction_row, direction_column in offsets:
            r, c = row + direction_row, col + direction_column
            while board.is_in_bounds((r, c)):
                target = board.get_piece((r, c))
                if target is None:
                    moves.append((r, c))
                elif target.color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += direction_row
                c += direction_column

        return moves


class King(Piece):
    """King: moves one square in any direction. Supports castling (kingside and queenside)."""

    def get_valid_moves(self, board) -> list[tuple[int, int]]:
        """Returns one-square moves plus castling squares if eligible.
        Check filtering and castling safety are handled in Board.get_legal_moves."""
        moves = []
        row, col = self.position

        offsets = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
        for direction_row, direction_column in offsets:
            destination = (row + direction_row, col + direction_column)
            if board.is_in_bounds(destination):
                target = board.get_piece(destination)
                if target is None or target.color != self.color:
                    moves.append(destination)

        # Castling: only available if king has not moved
        if not self.moved:
            # Kingside: rook on col 7, squares 5 and 6 empty
            if (board.get_piece((row, 7)) is not None and
                isinstance(board.get_piece((row, 7)), Rook) and
                not board.get_piece((row, 7)).moved and
                board.get_piece((row, 5)) is None and
                board.get_piece((row, 6)) is None):
                moves.append((row, 6))

            # Queenside: rook on col 0, squares 1, 2, and 3 empty
            if (board.get_piece((row, 0)) is not None and
                isinstance(board.get_piece((row, 0)), Rook) and
                not board.get_piece((row, 0)).moved and
                board.get_piece((row, 1)) is None and
                board.get_piece((row, 2)) is None and
                board.get_piece((row, 3)) is None):
                moves.append((row, 2))

        return moves

    def get_attacks(self, board) -> list[tuple[int, int]]:
        """Returns all adjacent squares the king controls (for opponent king exclusion)."""
        attacks = []
        row, col = self.position
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            dest = (row + dr, col + dc)
            if board.is_in_bounds(dest):
                target = board.get_piece(dest)
                if target is None or target.color != self.color:
                    attacks.append(dest)
        return attacks
