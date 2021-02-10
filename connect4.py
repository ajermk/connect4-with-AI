# pip3 install numpy
# * eliminate duplicate code (event handling for player 1 and 2 is essentially the same)
# * define player_color(piece): return (BLACK, RED, YELLOW)[piece]
# * merge the circle drawing code into a single line, making use of player_color
# * extract the event handling into a function
# * define a main function
# * turn = (turn + 1) % 2 (instead of the two lines)
# * fix the indentation of pygame.display.update() below the MOUSEMOVE
# https://pythonprogramming.net/pygame-buttons-part-1-button-rectangle/
# https://www.logolynx.com/topic/connect+4
# https://unsplash.com/photos/e6frrz-kh-0

import numpy as np
import win_state as win
import globals as gl
import random
import pygame
import sys
import math
import time

pygame.init()

width = gl.COLUMN_COUNT * gl.SQUARESIZE
height = (gl.ROW_COUNT+1) * gl.SQUARESIZE
screen = pygame.display.set_mode((width, height))

myfont = pygame.font.SysFont("monospace", 75)
clock = pygame.time.Clock();
boardImg = pygame.image.load('board.jpg')
logoImg = pygame.image.load('logo.png')

def create_board():
    board = np.zeros((gl.ROW_COUNT, gl.COLUMN_COUNT))
    return board

#a specific location gets filled by a piece
def drop_piece(board, row, colum, piece):
    board[row][colum] = piece

# check if top row isnt filled for a specific colum
def is_valid_location(board, colum):
    return board[gl.ROW_COUNT-1][colum] == 0

# check which row to put in a piece for a column
def get_next_open_row(board, colum):
    for row in range(gl.ROW_COUNT):
        if board[row][colum] == 0:
            return row

# change orientation of the board, [0,0] becomes [0,6]
def print_board(board):
   print(np.flip(board, 0))

#draws a blue rect and black circles on top
def draw_board(board, screen, boardImg):
    #pygame.draw.rect(screen, gl.BLUE, (colum*gl.SQUARESIZE, rows*gl.SQUARESIZE+gl.SQUARESIZE, gl.SQUARESIZE, gl.SQUARESIZE))
    screen.blit(boardImg, (0, gl.SQUARESIZE))
    # update each dropped piece
    for colum in range(gl.COLUMN_COUNT):
        for rows in range(gl.ROW_COUNT):
            #pygame.draw.circle(screen, gl.BROWN, (int(colum*gl.SQUARESIZE+gl.SQUARESIZE/2), height-int(rows*gl.SQUARESIZE+gl.SQUARESIZE/2)), int(gl.SQUARESIZE/2 - 5))
            if board[rows][colum] == gl.PLAYER1_PIECE:
                draw_piece(gl.YELLOW, screen, colum, rows)
            elif board[rows][colum] == gl.PLAYER2_PIECE:
                draw_piece(gl.RED, screen, colum, rows)
            else:
                draw_piece(gl.BLACK, screen, colum, rows)
    pygame.display.update()


def draw_piece(color, screen, colum, rows):
    pygame.draw.circle(screen, color, (int(colum*gl.SQUARESIZE+gl.SQUARESIZE/2), height-int(rows*gl.SQUARESIZE+gl.SQUARESIZE/2)), gl.RADIUS)

## ai, player2_piece is AI
def evaluate_window(window, piece):
    score = 0
    opp_piece = gl.PLAYER1_PIECE
    if piece == gl.PLAYER1_PIECE:
        opp_piece = gl.PLAYER2_PIECE
    if window.count(piece) == gl.WINNING_CONSECUTIVE_PIECES:
        score += 100
    elif (window.count(piece) == (gl.WINNING_CONSECUTIVE_PIECES - 1) ) and (window.count(gl.EMPTY) == 1):
        score += 10
    elif window.count(piece) == 2 and window.count(gl.EMPTY) == 2:
        score += 5
    if window.count(opp_piece) == 3 and window.count(gl.EMPTY) == 1:
        score -= 90

    return score
def score_position(board, piece):

    # score center column
    score = 0
    center_array = [int(i) for i in list (board[:, gl.COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 6
    ## horizontal score
    for rows in range(gl.ROW_COUNT):
        # get all colum positions in a single row
        # window sizes of 4
        # [start:end]
        row_array = [int(i) for i in list(board[rows,:])] # 7 row positions in a col
        for colum in range(gl.COLUMN_COUNT-(gl.WINNING_CONSECUTIVE_PIECES-1)): #row count - 1 = 3 so it doesnt check from 5th col bc no winning pos are there
            window = row_array[colum:colum+gl.WINDOW_LENGTH] # from to
            score += evaluate_window(window, piece)
    ## vertical
    for colum in range(gl.COLUMN_COUNT):
        colum_array = [int(i) for i in list(board[:,colum])]
        for rows in range(gl.ROW_COUNT-(gl.WINNING_CONSECUTIVE_PIECES-1)):
            window = colum_array[rows:rows+gl.WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # \
    for rows in range (gl.ROW_COUNT - (gl.WINNING_CONSECUTIVE_PIECES-1) ):
        for colum in range(gl.COLUMN_COUNT - (gl.WINNING_CONSECUTIVE_PIECES-1)):
            window = [board[rows+i][colum+i] for i in range(gl.WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    # /
    for rows in range (gl.ROW_COUNT - (gl.WINNING_CONSECUTIVE_PIECES-1) ):
        for colum in range(gl.COLUMN_COUNT - (gl.WINNING_CONSECUTIVE_PIECES-1)):
            window = [board[rows+3-i][colum+i] for i in range(gl.WINDOW_LENGTH)]
            score += evaluate_window(window, piece)
    return score

def is_terminal_node(board):
    return win.winning_state(board, gl.PLAYER1_PIECE) or win.winning_state(board, gl.PLAYER2_PIECE) or len(get_valid_locations(board)) == 0

def minmax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board) # array with columns where to drop
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if win.winning_state(board, gl.PLAYER2_PIECE):
                return (None, 10000000000000)
            elif win.winning_state(board,gl.PLAYER1_PIECE):
                return (None, -10000000000000)
            else: #game is over, no more valid moves
                return (None, 0)
        else: #depth 0
            return (None, score_position(board, gl.PLAYER2_PIECE))
    if maximizingPlayer:
        value = -math.inf
        col = random.choice(valid_locations)
        for colum in valid_locations:
            row = get_next_open_row(board, colum)
            b_copy = board.copy()
            drop_piece(b_copy, row, colum, gl.PLAYER2_PIECE)
            new_score = minmax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                col = colum
            #
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return col, value

    else: # minimizing player
        value = math.inf
        col = random.choice(valid_locations)
        for colum in valid_locations:
            row = get_next_open_row(board, colum)
            b_copy = board.copy()
            drop_piece(b_copy, row, colum, gl.PLAYER1_PIECE)
            new_score = minmax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                col = colum
            #
            beta = min(beta, value)
            if alpha >= beta:
                break
        return col, value

def get_valid_locations(board):
    valid_locations = []
    for colum in range(gl.COLUMN_COUNT):
        if is_valid_location(board, colum):
            valid_locations.append(colum)
    return valid_locations
# not used in minmax
def pick_best_move(board, piece):
    best_score = 0
    valid_locations = get_valid_locations(board)
    best_colum = random.choice(valid_locations)
    for colum in valid_locations:
        row = get_next_open_row(board, colum)
        temp_board = board.copy() # new memory location via .copy(), so you dont modify original board
        drop_piece(temp_board, row, colum, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_colum = colum
    return best_colum
## gui

def button(screen, msg, x, y, w, h, color, brighter_color, turn, action=None):
    smallText = pygame.font.SysFont("Chic",30)
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, gl.WHITE, (x-5, y-5, w+10, h+10))
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(screen, brighter_color, (x, y, w, h))
        if click[0] == 1 and action == game_loop:
            action(turn)
        elif click[0] == 1 and action == quitgame:
            action()
    else:
        pygame.draw.rect(screen, color, (x, y, w, h))

    textSurface, textRect = text_objects(msg, smallText, gl.BLACK)
    textRect.center = (x+(w/2), (y+(h/2)) )
    screen.blit(textSurface, textRect)


def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def text_display(msg, font, color, width, height):
    textSurface, textRect = text_objects(msg, myfont, color)
    textRect.center = (width, height)
    screen.blit(textSurface, textRect)

# returns false for keeping the game loop, true if it finds a winning state, none if placed incorrectly, which is changed to true in main game loop
def player_action(colum, piece, board, msg, color):
     #between 0 and 700


    if is_valid_location(board, colum):
        row = get_next_open_row(board, colum)
        drop_piece(board, row, colum, piece)
        if win.winning_state(board, piece):
            # erase the upper piece
            pygame.draw.rect(screen, gl.BLACK, (0,0, width, gl.SQUARESIZE))
            text_display(msg, myfont, color, width/2, 50)
            return True
    else:
        return None
    return False


def quitgame():
    pygame.quit()
    quit()

#game loop
def game_intro():
    intro = True

    while intro:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                quitgame()

        screen.fill(gl.BLACK)
        #text_display("Connect 4", myfont, gl.YELLOW, (width/2), (height-200)/2)
        screen.blit(logoImg, (-35, 100))
        button(screen, "START (PLAYER GOES FIRST)", 25,400,300,70,gl.YELLOW,gl.BRIGHT_YELLOW,0,game_loop)
        button(screen, "START (AI GOES FIRST)", 375,400,300,70,gl.RED,gl.BRIGHT_RED,1,game_loop)
        button(screen, "QUIT GAME", 250,525,200,70,gl.BLUE,gl.BRIGHT_BLUE, None, quitgame)
        pygame.display.update()


def game_loop(turn):

    board = create_board()
    game_over = False
    draw_board(board, screen, boardImg)

    while not game_over:
        # FPS
        clock.tick(60)


        # all events
        for event in pygame.event.get():
            #exit out of the game
            if event.type == pygame.QUIT:
                quitgame()

            #draw piece on top
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, gl.BLACK, (0,0, width, gl.SQUARESIZE))
                posx = event.pos[0]
                if turn == gl.PLAYER1_TURN:
                    pygame.draw.circle(screen, gl.YELLOW, (posx, int(gl.SQUARESIZE/2)), gl.RADIUS)
                # if turn == gl.PLAYER2_TURN:
                #    pygame.draw.circle(screen, gl.RED, (posx, int(gl.SQUARESIZE/2)), gl.RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                posx = event.pos[0]
                colum = int(math.floor(posx/gl.SQUARESIZE))
                # # p1 input
                if turn == gl.PLAYER1_TURN:
                    game_over = player_action(colum, gl.PLAYER1_PIECE, board, "PLAYER 1 WIN", gl.YELLOW)
                    if game_over == None:
                        game_over = False
                        continue
                    turn = (turn+1) % 2
                    draw_board(board, screen, boardImg)



                # p2 input
        #this is here to disable drawing of player piece on top
        pygame.draw.rect(screen, gl.BLACK, (0,0, width, gl.SQUARESIZE))
        if turn == gl.AI_TURN and not game_over:
            time.sleep(1)
            #colum = pick_best_move(board, gl.PLAYER2_PIECE)
            colum, minmax_score = minmax(board, 5, -math.inf, math.inf, True)
            #colum = random.randint(0,6)
            game_over = player_action(colum, gl.PLAYER2_PIECE, board, "PLAYER 2 WIN", gl.RED)
            if game_over == None:
                game_over = False
                continue
            turn = (turn+1) % 2
            

            draw_board(board, screen, boardImg)

            # alternate between turns, if it reaches 2 it goes back to 0, aka p1 turn

    time.sleep(5)

def main():
    while True:
        game_intro()

if __name__ == "__main__":
    main()
