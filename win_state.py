import globals as gl

def winning_state(board, piece):
    if (winning_state_hor(board,piece) or
        winning_state_vert(board, piece) or
        winning_state_diag1(board, piece) or
        winning_state_diag2(board, piece)):
        return True

def winning_state_vert(board, piece):
    # check horizontal, all columns in a single row
    for colum in range(gl.COLUMN_COUNT):
        consecutive = 0
        for rows in range(gl.ROW_COUNT):
            if board[rows][colum] == piece:
                consecutive += 1
            else:
                consecutive = 0
            if consecutive == gl.WINNING_CONSECUTIVE_PIECES:
                return True
    return False

def winning_state_hor(board, piece):
    # check vertical, all rows in a single column
    for rows in range(gl.ROW_COUNT):
        consecutive = 0
        for colum in range(gl.COLUMN_COUNT):
            if board[rows][colum] == piece:
                consecutive += 1
            else:
                consecutive = 0
            if consecutive == gl.WINNING_CONSECUTIVE_PIECES:
                return True
    return False

def winning_state_diag1(board, piece):
    # check \
    for cols in range(gl.COLUMN_COUNT):
        consecutive = 0
        for rows in range(gl.ROW_COUNT):
            if ((cols+rows < gl.COLUMN_COUNT) and board[rows][cols+rows]  == piece):
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= gl.WINNING_CONSECUTIVE_PIECES:
                return True
    for cols in range(gl.COLUMN_COUNT):
        consecutive = 0
        for rows in range(gl.ROW_COUNT):
            if ((cols+rows < gl.ROW_COUNT) and board[rows+cols][rows]  == piece):
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= gl.WINNING_CONSECUTIVE_PIECES:
                return True
    return False

def winning_state_diag2(board, piece):
    # check /
    for cols in range(gl.COLUMN_COUNT):
        consecutive = 0

        for rows in range(gl.ROW_COUNT):

            if ((cols-rows >= 0) and board[rows][cols-rows] == piece):
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= gl.WINNING_CONSECUTIVE_PIECES:
                return True
    rows =0
    cols = 0
    for rows in range(gl.ROW_COUNT):
        consecutive = 0
        iteration = 0
        for cols in range((gl.COLUMN_COUNT-1), -1, -1):
            if ((rows+iteration < gl.ROW_COUNT) and board[rows+iteration][cols]  == piece):
                consecutive += 1
            else:
                consecutive = 0
            if consecutive >= gl.WINNING_CONSECUTIVE_PIECES:
                return True
            iteration += 1
    return False
