// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCORES_KEY = 'sudokuTopScores';
const THEME_KEY = 'sudokuTheme';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let currentDifficulty = 'medium';
let hintsUsed = 0;
let completionRecorded = false;

function applyTheme(isDark) {
  document.body.classList.toggle('dark-mode', isDark);
  document.getElementById('dark-mode').checked = isDark;
  localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
  const seconds = (totalSeconds % 60).toString().padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function updateTimer() {
  document.getElementById('timer').innerText = `Time: ${formatTime(elapsedSeconds)}`;
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function loadScores() {
  try {
    const scores = JSON.parse(localStorage.getItem(SCORES_KEY) || '[]');
    return Array.isArray(scores) ? scores : [];
  } catch (error) {
    return [];
  }
}

function renderScores() {
  const scoreList = document.getElementById('top-scores');
  scoreList.innerHTML = '';
  const scores = loadScores();
  scores.forEach((score) => {
    const item = document.createElement('li');
    item.textContent = `${score.name} - ${formatTime(score.time)} - ${score.difficulty} - ${score.hints} hint${score.hints === 1 ? '' : 's'}`;
    scoreList.appendChild(item);
  });
}

function saveCompletedScore() {
  const name = window.prompt('Enter your name to save your score:');
  if (!name || !name.trim()) {
    return;
  }

  const scores = loadScores();
  scores.push({
    name: name.trim(),
    time: elapsedSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed
  });
  scores.sort((first, second) => first.time - second.time);
  try {
    localStorage.setItem(SCORES_KEY, JSON.stringify(scores.slice(0, 10)));
  } catch (error) {
    return;
  }
  renderScores();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        markConflicts();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.readOnly = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.readOnly = false;
        inp.classList.remove('prefilled');
      }
    }
  }
}

function hasBoardConflict(board, row, col, value) {
  if (value === 0) {
    return false;
  }

  for (let c = 0; c < SIZE; c++) {
    if (c !== col && board[row][c] === value) {
      return true;
    }
  }

  for (let r = 0; r < SIZE; r++) {
    if (r !== row && board[r][col] === value) {
      return true;
    }
  }

  const startRow = Math.floor(row / 3) * 3;
  const startCol = Math.floor(col / 3) * 3;
  for (let r = startRow; r < startRow + 3; r++) {
    for (let c = startCol; c < startCol + 3; c++) {
      if ((r !== row || c !== col) && board[r][c] === value) {
        return true;
      }
    }
  }

  return false;
}

function markConflicts() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const value = inputs[idx].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }

  for (let idx = 0; idx < inputs.length; idx++) {
    const input = inputs[idx];
    if (input.disabled) {
      input.classList.remove('incorrect');
      continue;
    }

    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);
    const value = input.value ? parseInt(input.value, 10) : 0;

    input.classList.remove('incorrect');
    if (value !== 0 && hasBoardConflict(board, row, col, value)) {
      input.classList.add('incorrect');
    }
  }
}

function isBoardComplete(board) {
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      if (puzzle[row][col] === 0 && board[row][col] === 0) {
        return false;
      }
    }
  }
  return true;
}

async function newGame() {
  startTimer();
  const difficulty = document.getElementById('difficulty').value;
  currentDifficulty = difficulty;
  hintsUsed = 0;
  completionRecorded = false;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}

async function useHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--error-color)';
    msg.innerText = data.error;
    return;
  }

  const idx = data.row * SIZE + data.col;
  const input = inputs[idx];
  input.value = data.value;
  input.disabled = true;
  input.readOnly = true;
  input.classList.remove('incorrect');
  input.classList.add('prefilled');
  hintsUsed += 1;
  msg.style.color = 'var(--success-color)';
  msg.innerText = 'Hint revealed.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--error-color)';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0 && isBoardComplete(board)) {
    stopTimer();
    if (!completionRecorded) {
      completionRecorded = true;
      saveCompletedScore();
    }
    msg.style.color = 'var(--success-color)';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = 'var(--error-color)';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  renderScores();
  const darkMode = localStorage.getItem(THEME_KEY) === 'dark';
  applyTheme(darkMode);
  document.getElementById('dark-mode').addEventListener('change', (event) => {
    applyTheme(event.target.checked);
  });
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', useHint);
  // initialize
  newGame();
});
