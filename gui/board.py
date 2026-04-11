import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame as py 

from engine import board
from engine import moves
from engine import pieces


WIDTH = HEIGHT = 512
DIMENSION = 8
S_SIZE = HEIGHT // DIMENSION
MAX_FPS = 20
IMAGES = {}


def images():
    pieces = ["bP", "bR", "bKN", "bB", "bQ", "bK", "wP", "wR", "wKN", "wB", "wQ", "wK"]
    for p in pieces:
        path = os.path.join(os.path.dirname(__file__), "Images", p + ".png")
        IMAGES[p] = py.transform.scale(py.image.load(path), (S_SIZE, S_SIZE))


def main():
    py.init()
    screen = py.display.set_mode((WIDTH, HEIGHT))
    clock = py.time.Clock()
    screen.fill(py.Color("white"))
    gs = board.Board()
    images()
    running = True
    s_selected =  () #Keep track of the last square selected
    p_clicks = [] #Keep track of player clicks
    while running:
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
            elif e.type == py.MOUSEBUTTONDOWN:
                location = py.mouse.get_pos()
                col = location[0] // S_SIZE
                row = location[1] // S_SIZE
                if s_selected == (row,col): #For if the user clicks the same square twice
                    s_selected = () #Deselects the square
                    p_clicks = []  #Clears the player clicks
                else:
                    s_selected = (row, col)
                    p_clicks.append(s_selected)
                if len(p_clicks) == 2:
                    piece = gs.board[p_clicks[0][0]][p_clicks[0][1]]
                    
                    if piece is None:  # first click was an empty square
                        s_selected = ()
                        p_clicks = []
                    elif (gs.wtomove and piece.color == 'w') or (not gs.wtomove and piece.color == 'b'):
                        valid_moves = piece.get_valid_moves(gs)
                        destination = p_clicks[1]
                        
                        if destination in valid_moves:
                            move = moves.Moves(p_clicks[0], p_clicks[1], gs.board)
                            gs.move(move)
                            piece.moved = True
                            piece.position = destination
                        
                        s_selected = ()
                        p_clicks = []
                    else:
                        s_selected = ()
                        p_clicks = []
        VisualGameState(screen, gs, s_selected)
        clock.tick(MAX_FPS)
        py.display.flip()

def VisualGameState(screen, gs, s_selected):
    VisualBoard(screen)
    VisualHighlights(screen, gs, s_selected)  # after board, before pieces
    VisualPieces(screen, gs.board)

def VisualHighlights(screen, gs, s_selected):
    # highlight selected square in yellow
    if s_selected != ():
        row, col = s_selected
        highlight = py.Surface((S_SIZE, S_SIZE))
        highlight.set_alpha(100)
        highlight.fill(py.Color("yellow"))
        screen.blit(highlight, (col * S_SIZE, row * S_SIZE))


def VisualBoard(screen):
    colors = [py.Color("white"), py.Color("light blue")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            py.draw.rect(screen, color, py.Rect(c*S_SIZE, r*S_SIZE, S_SIZE, S_SIZE))

def VisualPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece is not None:
                key = piece.get_image_key()
                screen.blit(IMAGES[key], py.Rect(c*S_SIZE, r*S_SIZE, S_SIZE, S_SIZE))

if __name__ == "__main__":
    main()