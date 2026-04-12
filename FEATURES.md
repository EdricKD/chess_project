# Features

## Core Chess Rules

- **All piece movement**: Pawns, Knights, Bishops, Rooks, Queens, and Kings all move according to standard chess rules.
- **Legal move filtering**: Every pseudo-legal move is simulated to confirm the moving player's king is not left in check. Illegal moves are never shown or accepted.
- **Check detection**: The king's square is tested against all opposing piece attack patterns each turn. The king's square is highlighted red when in check.
- **Checkmate**: Detected when the active player is in check and has no legal moves. The game freezes and a result overlay is displayed.
- **Stalemate**: Detected when the active player is not in check but has no legal moves. Counts as a draw.

## Special Moves

- **En passant**: The en passant target square is tracked after every double pawn push. A pawn capturing en passant correctly removes the captured pawn from its original rank.
- **Castling**: Both kingside and queenside castling are supported. Castling is blocked if the king has moved, the rook has moved, any square between them is occupied, the king is in check, or the king would pass through an attacked square.
- **Pawn promotion**: When a pawn reaches the back rank, the board freezes and a panel of four choices (Queen, Rook, Bishop, Knight) is shown. The pawn is replaced by the chosen piece.

## Undo

- **Undo (Z key)**: Reverts the last move, restoring the captured piece, en passant state, castling eligibility, and the active turn. En passant captures and castling rook moves are both correctly undone.

## Board Display

- **Board flip**: The board rotates 180° each turn so the active player always views from their own side.
- **Valid move highlights**: Clicking a piece shows dots on empty squares it can legally move to, and a red overlay on squares where it can capture.
- **Selected square highlight**: The currently selected square is tinted green.

## Side Panel and Menu

- **Score tracking**: Win/loss/draw counts persist across games within the same session.
- **New Game**: Starts a fresh standard game, carrying over the current score.
- **Freestyle mode**: Starts a game with randomly shuffled back ranks (Chess960 style) for both players.
- **Resign**: Either player can resign from the menu. A confirmation step prevents accidental resignations.

## Chess Clock

- **Time controls**: Choose from 3 min, 5 min, 10 min, or Unlimited before starting a game.
- **Per-player countdown**: Each player's clock counts down only on their turn. The active player's time is shown in white; the inactive player's in grey.
- **Timeout**: When a player's clock reaches zero, the opponent wins and the result is displayed.
