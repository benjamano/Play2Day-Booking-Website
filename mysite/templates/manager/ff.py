
# Create the game board
board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

# Display the game board
def display_board():
    print(board[0][0] + '|' + board[0][1] + '|' + board[0][2])
    print('-+-+-')
    print(board[1][0] + '|' + board[1][1] + '|' + board[1][2])
    print('-+-+-')
    print(board[2][0] + '|' + board[2][1] + '|' + board[2][2])

# Check if the game has been won
def check_win():
    # Check rows
    for row in board:
        if row[0] == row[1] == row[2] and row[0] != ' ':
            return True
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != ' ':
            return True
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != ' ':
        return True
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != ' ':
        return True
    return False

# Check if the game is tied
def check_tie():
    for row in board:
        for col in row:
            if col == ' ':
                return False
    return True

# Start the game
def play_game():
    # Initialize variables
    player = 'X'
    game_over = False
    
    # Loop until the game is over
    while not game_over:
        # Display the game board
        display_board()
        
        # Ask the user for their move
        valid_move = False
        while not valid_move:
            row = int(input('Enter row (1-3): ')) - 1
            col = int(input('Enter column (1-3): ')) - 1
            if row < 0 or row > 2 or col < 0 or col > 2:
                print('Invalid position. Try again.')
            elif board[row][col] != ' ':
                print('Position already taken. Try again.')
            else:
                valid_move = True
        
        # Place the user's symbol on the board
        board[row][col] = player
        
        # Check if the game has been won or tied
        if check_win():
            display_board()
            print(player + ' wins!')
            game_over = True
        elif check_tie():
            display_board()
            print('Tie game!')
            game_over = True
        else:
            # Switch to the other player's turn
            if player == 'X':
                player = 'O'
            else:
                player = 'X'

# Start the game
play_game()
