from flask import Flask, request, jsonify
import random

app = Flask(__name__)

BOARD_SIZE = 8
SHIP_SIZES = [2, 2, 2, 3, 3, 4]
SHIP_SYMBOL = 'S'
HIT_SYMBOL = 'X'
MISS_SYMBOL = 'O'
EMPTY_SYMBOL = '~'

def create_board():
    return [[EMPTY_SYMBOL] * BOARD_SIZE for _ in range(BOARD_SIZE)]

def place_ships_randomly(board):
    ships = []
    for size in SHIP_SIZES:
        placed = False
        while not placed:
            direction = random.choice(['H', 'V'])
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)

            if direction == 'H' and col + size <= BOARD_SIZE:
                if all(board[row][col + i] == EMPTY_SYMBOL for i in range(size)):
                    ship_positions = [(row, col + i) for i in range(size)]
                    for i in range(size):
                        board[row][col + i] = SHIP_SYMBOL
                    ships.append(ship_positions)
                    placed = True
            elif direction == 'V' and row + size <= BOARD_SIZE:
                if all(board[row + i][col] == EMPTY_SYMBOL for i in range(size)):
                    ship_positions = [(row + i, col) for i in range(size)]
                    for i in range(size):
                        board[row + i][col] = SHIP_SYMBOL
                    ships.append(ship_positions)
                    placed = True
    return ships

@app.route('/start', methods=['POST'])
def start_game():
    player_board = create_board()
    computer_board = create_board()
    computer_ships = place_ships_randomly(computer_board)
    computer_ships1 = [list(map(tuple, ship)) for ship in computer_ships]  # Convert ship coordinates to tuples

    return jsonify({
        'player_board': player_board,
        'computer_board': computer_board,
        'computer_ships': computer_ships,
        'computer_ships1': computer_ships1,
        'player_hits': 0  # Add hit counter
    })

@app.route('/player_click', methods=['POST'])
def player_click():
    data = request.json
    row = data['row']
    col = data['col']
    computer_board = data['computer_board']
    player_view_board = data['player_view_board']
    computer_ships = data['computer_ships']
    computer_ships1 = [list(map(tuple, ship)) for ship in computer_ships]
    player_hits = data['player_hits']  # Retrieve current hit count

    print(f"Received click at ({row}, {col})")
    print(f"Computer board state: {computer_board}")
    print(f"Player view board state: {player_view_board}")
    print(f"Computer ships (tuple): {computer_ships1}")

    if computer_board[row][col] == SHIP_SYMBOL:
        player_view_board[row][col] = HIT_SYMBOL
        computer_board[row][col] = HIT_SYMBOL  # Update the computer's board as well
        player_hits += 1  # Increment hit counter
        print("Hit detected at:", row, col)

        print(f"Player hits: {player_hits}, Total ship segments: {sum(SHIP_SIZES)}")  # Debugging print

        # Check if all ships have been sunk
        if player_hits == sum(SHIP_SIZES):
            print("All ships have been sunk. Player wins!")
            return jsonify({
                'result': 'win',
                'player_view_board': player_view_board,
                'computer_board': computer_board,
                'computer_ships': computer_ships,
                'computer_ships1': computer_ships1,
                'player_hits': player_hits
            })
        
        for ship in computer_ships1:
            if (row, col) in ship:
                print(f"Hit is part of the ship: {ship}")
                if all(computer_board[r][c] == HIT_SYMBOL for r, c in ship):
                    print("Ship sunk:", ship)
                    return jsonify({
                        'result': 'sunk',
                        'player_view_board': player_view_board,
                        'computer_board': computer_board,
                        'computer_ships': computer_ships,
                        'computer_ships1': computer_ships1,
                        'player_turn': True,
                        'player_hits': player_hits
                    })

        return jsonify({
            'result': 'hit',
            'player_view_board': player_view_board,
            'computer_board': computer_board,
            'computer_ships': computer_ships,
            'computer_ships1': computer_ships1,
            'player_turn': True,
            'player_hits': player_hits
        })
    else:
        player_view_board[row][col] = MISS_SYMBOL
        print("Miss detected at:", row, col)
        return jsonify({
            'result': 'continue',
            'player_view_board': player_view_board,
            'computer_board': computer_board,
            'computer_ships': computer_ships,
            'computer_ships1': computer_ships1,
            'player_turn': False,
            'player_hits': player_hits
        })

@app.route('/place_ship', methods=['POST'])
def place_ship():
    data = request.json
    row = data['row']
    col = data['col']
    size = data['size']
    direction = data['direction']
    player_board = data['player_board']

    if direction == 'H' and col + size <= BOARD_SIZE:
        if all(player_board[row][col + i] == EMPTY_SYMBOL for i in range(size)):
            for i in range(size):
                player_board[row][col + i] = SHIP_SYMBOL
            return jsonify({'result': 'success', 'player_board': player_board})
    elif direction == 'V' and row + size <= BOARD_SIZE:
        if all(player_board[row + i][col] == EMPTY_SYMBOL for i in range(size)):
            for i in range(size):
                player_board[row + i][col] = SHIP_SYMBOL
            return jsonify({'result': 'success', 'player_board': player_board})
    return jsonify({'result': 'fail'})

if __name__ == '__main__':
    app.run(debug=True)
