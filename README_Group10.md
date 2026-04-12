# Chess Project

A two-player chess game built with Python and pygame.

## Requirements

- Python 3.10+
- pygame (`pip install pygame`)

## Running the Game

```
python main.py
```

## Controls

Input -> Action 

Left-click a piece       -> Select it (valid moves are highlighted) 
Left-click a destination -> Move the selected piece 
Z                        -> Undo the last move 
Escape                   -> Open / close the side menu 

## Project Structure

```
chess_project/
├── main.py              # Entry point
├── engine/
│   ├── board.py         # Game state, move application, check/checkmate/stalemate
│   ├── pieces.py        # Piece classes and movement rules
│   └── moves.py         # Move representation and algebraic notation
└── gui/
    ├── board.py         # pygame rendering and event loop
    └── Images/          # Piece sprite PNGs 
```

## Save / Load

Use **Save Game** in the menu to write the current position to `saves/save.json`.  
Use **Load Game** to restore it (clocks and move history are fully restored).

