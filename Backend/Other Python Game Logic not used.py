import tkinter as tk
from tkinter import messagebox
import random

BOARD_SIZE = 8
SHIP_SIZES = [2, 2, 2, 3, 3, 4]
SHIP_SYMBOL = 'S'
HIT_SYMBOL = 'X'
MISS_SYMBOL = 'O'
EMPTY_SYMBOL = '~'

class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Battleship Game")
        
        self.player_board = self.create_board()
        self.computer_board = self.create_board()
        self.player_view_board = self.create_board()

        self.place_ships_randomly(self.computer_board)
        
        self.player_ships_to_place = SHIP_SIZES[:]
        self.current_direction = 'H'
        self.is_placing_ships = True
        self.player_turn = False

        self.create_widgets()

    def create_board(self):
        return [[EMPTY_SYMBOL] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    
    def is_ship_sunk(self, board, ship_positions):
        return all(board[row][col] == HIT_SYMBOL for row, col in ship_positions)

    def place_ships_randomly(self, board):
        self.computer_ships = []
        for size in SHIP_SIZES:
            placed = False
            while not placed:
                direction = random.choice(['H', 'V'])
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - 1)

                if direction == 'H' and col + size <= BOARD_SIZE:
                    if all(board[row][col + i] == EMPTY_SYMBOL for i in range(size)):
                        ship_positions = []
                        for i in range(size):
                            board[row][col + i] = SHIP_SYMBOL
                            ship_positions.append((row, col + i))
                        self.computer_ships.append(ship_positions)
                        placed = True
                elif direction == 'V' and row + size <= BOARD_SIZE:
                    if all(board[row + i][col] == EMPTY_SYMBOL for i in range(size)):
                        ship_positions = []
                        for i in range(size):
                            board[row + i][col] = SHIP_SYMBOL
                            ship_positions.append((row + i, col))
                        self.computer_ships.append(ship_positions)
                        placed = True

    def create_widgets(self):
        self.frames = {}
        self.buttons = {}

        for frame_name, board, command in [("player", self.player_board, self.player_place_ship), ("computer", self.player_view_board, self.player_click)]:
            frame = tk.Frame(self.root)
            frame.pack(side=tk.LEFT, padx=10, pady=10)
            self.frames[frame_name] = frame

            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    btn = tk.Button(frame, width=2, height=1, text=board[row][col],
                                    command=lambda r=row, c=col, cmd=command: cmd(r, c) if cmd else None)
                    btn.grid(row=row, column=col)
                    self.buttons[(frame_name, row, col)] = btn
        
        self.direction_button = tk.Button(self.root, text="Rotate Ship (H)", command=self.rotate_ship)
        self.direction_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.start_button = tk.Button(self.root, text="Start Game", state=tk.DISABLED, command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=10, pady=10)

    def rotate_ship(self):
        if self.current_direction == 'H':
            self.current_direction = 'V'
            self.direction_button.config(text="Rotate Ship (V)")
        else:
            self.current_direction = 'H'
            self.direction_button.config(text="Rotate Ship (H)")

    def player_place_ship(self, row, col):
        if not self.is_placing_ships:
            return

        if not self.player_ships_to_place:
            return

        size = self.player_ships_to_place[0]
        if self.can_place_ship(self.player_board, row, col, size, self.current_direction):
            self.place_ship(self.player_board, row, col, size, self.current_direction)
            self.player_ships_to_place.pop(0)

            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    self.buttons[("player", r, c)].config(text=self.player_board[r][c])

            if not self.player_ships_to_place:
                self.is_placing_ships = False
                self.start_button.config(state=tk.NORMAL)

    def can_place_ship(self, board, row, col, size, direction):
        if direction == 'H':
            if col + size > BOARD_SIZE:
                return False
            return all(board[row][col + i] == EMPTY_SYMBOL for i in range(size))
        else:
            if row + size > BOARD_SIZE:
                return False
            return all(board[row + i][col] == EMPTY_SYMBOL for i in range(size))

    def place_ship(self, board, row, col, size, direction):
        if direction == 'H':
            for i in range(size):
                board[row][col + i] = SHIP_SYMBOL
        else:
            for i in range(size):
                board[row + i][col] = SHIP_SYMBOL

    def start_game(self):
        self.start_button.config(state=tk.DISABLED)
        self.direction_button.pack_forget()
        self.player_turn = True

    def player_click(self, row, col):
        if not self.player_turn or self.player_view_board[row][col] != EMPTY_SYMBOL:
            return

        if self.computer_board[row][col] == SHIP_SYMBOL:
            self.player_view_board[row][col] = HIT_SYMBOL
            self.computer_board[row][col] = HIT_SYMBOL
            self.buttons[("computer", row, col)].configure(text=HIT_SYMBOL, bg='red')
            
            sunk_ship = None
            for ship in self.computer_ships:
                if (row, col) in ship:
                    if self.is_ship_sunk(self.player_view_board, ship):
                        sunk_ship = ship
                        break

            if sunk_ship:
                messagebox.showinfo("Battleship", "You sank a ship!")

            if self.check_win(self.computer_board):
                messagebox.showinfo("Battleship", "Congratulations! You sank all the computer's ships!")
                self.root.quit()
        else:
            self.player_view_board[row][col] = MISS_SYMBOL
            self.buttons[("computer", row, col)].configure(text=MISS_SYMBOL, bg='blue')
            self.player_turn = False
            self.root.after(1000, self.computer_turn)

    def computer_turn(self):
        while True:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            if self.player_board[row][col] in [EMPTY_SYMBOL, SHIP_SYMBOL]:
                if self.player_board[row][col] == SHIP_SYMBOL:
                    self.player_board[row][col] = HIT_SYMBOL
                    self.buttons[("player", row, col)].configure(text=HIT_SYMBOL, bg='red')
                    if self.check_win(self.player_board):
                        messagebox.showinfo("Battleship", "Computer wins! Better luck next time.")
                        self.root.quit()
                    else:
                        # Schedule another turn for the computer after 1 second
                        self.root.after(1000, self.computer_turn)
                    return  # Exit the function if it's a hit to prevent further execution
                else:
                    self.player_board[row][col] = MISS_SYMBOL
                    self.buttons[("player", row, col)].configure(text=MISS_SYMBOL, bg='blue')
                break

        # Set player's turn to True if the computer misses
        self.player_turn = True

    def check_win(self, board):
        return all(cell != SHIP_SYMBOL for row in board for cell in row)

def main():
    root = tk.Tk()
    game = BattleshipGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
