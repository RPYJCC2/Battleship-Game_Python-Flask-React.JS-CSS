import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import AudioPlayer from './components/AudioPlayer';

const BOARD_SIZE = 8;
const EMPTY_SYMBOL = '~';
const HIT_SYMBOL = 'X';
const MISS_SYMBOL = 'O';
const SHIP_SYMBOL = 'S';
const SHIP_SIZES = [2, 2, 2, 3, 3, 4];

const createBoard = () => {
  return Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(EMPTY_SYMBOL));
};

const App = () => {
  const [playerBoard, setPlayerBoard] = useState(createBoard());
  const [computerBoard, setComputerBoard] = useState(createBoard());
  const [playerViewBoard, setPlayerViewBoard] = useState(createBoard());
  const [isPlayerTurn, setIsPlayerTurn] = useState(true);
  const [computerShips, setComputerShips] = useState([]);
  const [computerShips1, setComputerShips1] = useState([]);
  const [isPlacing, setIsPlacing] = useState(true);
  const [currentShip, setCurrentShip] = useState(SHIP_SIZES[0]);
  const [direction, setDirection] = useState('H');
  const [shipIndex, setShipIndex] = useState(0);
  const [playerHits, setPlayerHits] = useState(0);  // Add hit counter

  useEffect(() => {
    axios.post('/start')
      .then(response => {
        setPlayerBoard(response.data.player_board);
        setComputerBoard(response.data.computer_board);
        setPlayerViewBoard(createBoard());
        setComputerShips(response.data.computer_ships);
        setComputerShips1(response.data.computer_ships1);  // Set computer_ships1
        setPlayerHits(0);  // Initialize hit counter
      });
  }, []);

  const handleCellClick = (row, col) => {
    if (isPlacing) {
      placeShip(row, col);
    } else {
      if (!isPlayerTurn || playerViewBoard[row][col] !== EMPTY_SYMBOL) {
        return;
      }

      axios.post('/player_click', {
        row,
        col,
        computer_board: computerBoard,
        player_view_board: playerViewBoard,
        computer_ships: computerShips,
        player_hits: playerHits  // Pass the current hit count
      })
      .then(response => {
        console.log("Response data:", response.data);  // Debugging print
        setPlayerViewBoard(response.data.player_view_board);
        setComputerBoard(response.data.computer_board);
        setComputerShips(response.data.computer_ships);
        setComputerShips1(response.data.computer_ships1);  // Set computer_ships1
        setPlayerHits(response.data.player_hits);  // Update hit counter

        if (response.data.result === 'win') {
          console.log("Player wins!");  // Debugging print
          alert('Congratulations! You sank all the computer\'s ships!');
        } else if (response.data.result === 'sunk') {
          alert('You sank a ship!');
          setIsPlayerTurn(true);
        } else if (response.data.result === 'hit') {
          setIsPlayerTurn(true);
        } else if (response.data.result === 'continue') {
          setIsPlayerTurn(false);
          setTimeout(() => computerTurn(), 1000); // Simulate computer turn after a delay
        }
      });
    }
  };

  const placeShip = (row, col) => {
    axios.post('/place_ship', {
      row,
      col,
      size: currentShip,
      direction: direction,
      player_board: playerBoard
    })
    .then(response => {
      if (response.data.result === 'success') {
        setPlayerBoard(response.data.player_board);
        if (shipIndex < SHIP_SIZES.length - 1) {
          setShipIndex(shipIndex + 1);
          setCurrentShip(SHIP_SIZES[shipIndex + 1]);
        } else {
          setIsPlacing(false);
        }
      } else {
        alert('Invalid placement. Try again.');
      }
    });
  };

  const toggleDirection = () => {
    setDirection(direction === 'H' ? 'V' : 'H');
  };

  const computerTurn = () => {
    let row, col;
    while (true) {
      row = Math.floor(Math.random() * BOARD_SIZE);
      col = Math.floor(Math.random() * BOARD_SIZE);
      if (playerBoard[row][col] === EMPTY_SYMBOL || playerBoard[row][col] === SHIP_SYMBOL) {
        break;
      }
    }

    const newPlayerBoard = playerBoard.map(row => row.slice()); // Deep copy of player board so AI hits and misses get color
    if (newPlayerBoard[row][col] === SHIP_SYMBOL) {
      newPlayerBoard[row][col] = HIT_SYMBOL;
    } else {
      newPlayerBoard[row][col] = MISS_SYMBOL;
    }
    setPlayerBoard(newPlayerBoard);

    if (checkWin(newPlayerBoard)) {
      alert('Computer wins! Better luck next time.');
    } else {
      setIsPlayerTurn(true);
    }
  };

  const checkWin = (board) => {
    return board.every(row => row.every(cell => cell !== SHIP_SYMBOL));
  };

  return (
    <div className="App">
      <h1>Battleship Game</h1>
      {isPlacing && (
        <div>
          <h2>Place Your Ships</h2>
          <button onClick={toggleDirection}>
            Toggle Direction (Current: {direction})
          </button>
          <p>Placing ship of size {currentShip}</p>
        </div>
      )}
      <div className="boards">
        <div className="board-container">
          <h2>Player Board</h2>
          <div className="board">
            {playerBoard.map((row, rowIndex) => (
              <div key={rowIndex} className="row">
                {row.map((cell, colIndex) => (
                  <div
                    key={colIndex}
                    className={`cell ${cell === SHIP_SYMBOL ? 'ship-cell' : cell === HIT_SYMBOL ? 'hit-cell' : cell === MISS_SYMBOL ? 'miss-cell' : ''}`}
                    onClick={() => isPlacing && handleCellClick(rowIndex, colIndex)}
                  >
                    {cell}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
        {!isPlacing && (
          <div className="board-container">
            <h2>Computer Board</h2>
            <div className="board">
              {playerViewBoard.map((row, rowIndex) => (
                <div key={rowIndex} className="row">
                  {row.map((cell, colIndex) => (
                    <div
                      key={colIndex}
                      className={`cell ${cell === HIT_SYMBOL ? 'hit-cell' : cell === MISS_SYMBOL ? 'miss-cell' : ''}`}
                      onClick={() => handleCellClick(rowIndex, colIndex)}
                    >
                      {cell}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      <AudioPlayer />
    </div>
  );
};

export default App;
