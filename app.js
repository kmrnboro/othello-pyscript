const EMPTY = 0;
const BLACK = 1;
const WHITE = 2;
const SIZE = 8;

let board = [];
let currentTurn = BLACK;
let history = [];
let aiBusy = false;

const directions = [
  [-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]
];

function newBoard() {
  const b = Array.from({ length: SIZE }, () => Array(SIZE).fill(EMPTY));
  b[3][3] = WHITE;
  b[4][4] = WHITE;
  b[3][4] = BLACK;
  b[4][3] = BLACK;
  return b;
}

function cloneBoard(b) {
  return b.map(row => row.slice());
}

function opponent(color) {
  return color === BLACK ? WHITE : BLACK;
}

function isValidMoveOn(b, r, c, color) {
  if (r < 0 || r >= SIZE || c < 0 || c >= SIZE || b[r][c] !== EMPTY) return false;
  const opp = opponent(color);
  for (const [dr, dc] of directions) {
    let nr = r + dr;
    let nc = c + dc;
    let foundOpp = false;
    while (nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE && b[nr][nc] === opp) {
      foundOpp = true;
      nr += dr;
      nc += dc;
    }
    if (foundOpp && nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE && b[nr][nc] === color) {
      return true;
    }
  }
  return false;
}

function validMovesOn(b, color) {
  const moves = [];
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      if (isValidMoveOn(b, r, c, color)) moves.push([r, c]);
    }
  }
  return moves;
}

function applyMoveOn(b, r, c, color) {
  if (!isValidMoveOn(b, r, c, color)) return null;
  const next = cloneBoard(b);
  next[r][c] = color;
  const opp = opponent(color);

  for (const [dr, dc] of directions) {
    const flips = [];
    let nr = r + dr;
    let nc = c + dc;
    while (nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE && next[nr][nc] === opp) {
      flips.push([nr, nc]);
      nr += dr;
      nc += dc;
    }
    if (flips.length && nr >= 0 && nr < SIZE && nc >= 0 && nc < SIZE && next[nr][nc] === color) {
      for (const [fr, fc] of flips) next[fr][fc] = color;
    }
  }
  return next;
}

function counts(b = board) {
  let black = 0;
  let white = 0;
  for (const row of b) {
    for (const cell of row) {
      if (cell === BLACK) black++;
      else if (cell === WHITE) white++;
    }
  }
  return [black, white];
}

function gameOverOn(b) {
  return validMovesOn(b, BLACK).length === 0 && validMovesOn(b, WHITE).length === 0;
}

function countFlipsOn(b, r, c, color) {
  if (!isValidMoveOn(b, r, c, color)) return -1;
  const next = applyMoveOn(b, r, c, color);
  let before = 0;
  let after = 0;
  for (const row of b) before += row.filter(v => v === color).length;
  for (const row of next) after += row.filter(v => v === color).length;
  return after - before - 1;
}

const weights = [
  [100,-20,10,5,5,10,-20,100],
  [-20,-50,-2,-2,-2,-2,-50,-20],
  [10,-2,-1,-1,-1,-1,-2,10],
  [5,-2,-1,-1,-1,-1,-2,5],
  [5,-2,-1,-1,-1,-1,-2,5],
  [10,-2,-1,-1,-1,-1,-2,10],
  [-20,-50,-2,-2,-2,-2,-50,-20],
  [100,-20,10,5,5,10,-20,100]
];

function evaluate(b, player) {
  const opp = opponent(player);
  let score = 0;
  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      if (b[r][c] === player) score += 1 + weights[r][c];
      else if (b[r][c] === opp) score -= 1 + weights[r][c];
    }
  }
  const mobility = validMovesOn(b, player).length - validMovesOn(b, opp).length;
  return score + mobility * 3;
}

function minimax(b, turn, depth, alpha, beta, maximizingPlayer) {
  if (depth === 0 || gameOverOn(b)) return evaluate(b, maximizingPlayer);
  const moves = validMovesOn(b, turn);
  if (moves.length === 0) {
    return minimax(b, opponent(turn), depth - 1, alpha, beta, maximizingPlayer);
  }

  if (turn === maximizingPlayer) {
    let best = -Infinity;
    for (const [r, c] of moves) {
      const next = applyMoveOn(b, r, c, turn);
      best = Math.max(best, minimax(next, opponent(turn), depth - 1, alpha, beta, maximizingPlayer));
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  }

  let best = Infinity;
  for (const [r, c] of moves) {
    const next = applyMoveOn(b, r, c, turn);
    best = Math.min(best, minimax(next, opponent(turn), depth - 1, alpha, beta, maximizingPlayer));
    beta = Math.min(beta, best);
    if (beta <= alpha) break;
  }
  return best;
}

function bestMove(b, color, depth = 3) {
  const moves = validMovesOn(b, color);
  if (!moves.length) return null;
  let best = moves[0];
  let bestScore = -Infinity;
  let alpha = -Infinity;
  for (const [r, c] of moves) {
    const next = applyMoveOn(b, r, c, color);
    const score = minimax(next, opponent(color), depth - 1, alpha, Infinity, color);
    if (score > bestScore) {
      bestScore = score;
      best = [r, c];
    }
    alpha = Math.max(alpha, bestScore);
  }
  return best;
}

function aiColor() {
  return document.getElementById('player-color').value === 'black' ? WHITE : BLACK;
}

function renderBoard() {
  const boardEl = document.getElementById('game-board');
  if (!boardEl.children.length) {
    for (let r = 0; r < SIZE; r++) {
      for (let c = 0; c < SIZE; c++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.row = String(r);
        cell.dataset.col = String(c);
        const piece = document.createElement('div');
        piece.className = 'piece';
        cell.appendChild(piece);
        cell.addEventListener('click', () => handleCellClick(r, c));
        boardEl.appendChild(cell);
      }
    }
  }

  for (const cell of boardEl.children) {
    const r = Number(cell.dataset.row);
    const c = Number(cell.dataset.col);
    cell.classList.remove('black', 'white', 'valid-move', 'best-move');
    if (board[r][c] === BLACK) cell.classList.add('black');
    else if (board[r][c] === WHITE) cell.classList.add('white');
  }

  highlightMoves();
  updateStatus();
}

function updateStatus(message = null) {
  const status = document.getElementById('status');
  const [black, white] = counts();
  if (message) {
    status.textContent = message;
    return;
  }
  if (gameOverOn(board)) {
    const result = black > white ? 'くろのかち！' : white > black ? 'しろのかち！' : 'ひきわけ！';
    status.textContent = `対局終了！ ${result} (くろ:${black} - しろ:${white})`;
    return;
  }
  const turn = currentTurn === BLACK ? 'くろ' : 'しろ';
  status.textContent = `じゅんばん: ${turn} | くろ: ${black} | しろ: ${white}`;
}

function highlightMoves() {
  const hintId = currentTurn === BLACK ? 'hint-black' : 'hint-white';
  const mode = document.getElementById(hintId).value;
  if (mode === 'none') return;

  const moves = validMovesOn(board, currentTurn);
  const best = mode === 'best' ? bestMove(board, currentTurn, 3) : null;
  for (const [r, c] of moves) {
    const idx = r * SIZE + c;
    const cell = document.getElementById('game-board').children[idx];
    cell.classList.add('valid-move');
    if (best && r === best[0] && c === best[1]) cell.classList.add('best-move');
  }
}

async function handleCellClick(r, c) {
  if (aiBusy || gameOverOn(board)) return;
  const level = document.getElementById('ai-level').value;
  if (level !== 'none' && currentTurn === aiColor()) return;
  await makeMove(r, c);
}

async function makeMove(r, c) {
  const next = applyMoveOn(board, r, c, currentTurn);
  if (!next) return false;
  history.push({ board: cloneBoard(board), turn: currentTurn });
  board = next;
  currentTurn = opponent(currentTurn);
  renderBoard();
  await continueGame();
  return true;
}

async function continueGame() {
  if (gameOverOn(board)) {
    renderBoard();
    return;
  }

  if (validMovesOn(board, currentTurn).length === 0) {
    const passed = currentTurn === BLACK ? 'くろ' : 'しろ';
    currentTurn = opponent(currentTurn);
    renderBoard();
    updateStatus(`${passed}はパスです`);
    await delay(700);
    renderBoard();
  }

  const level = document.getElementById('ai-level').value;
  if (level !== 'none' && currentTurn === aiColor() && !gameOverOn(board)) {
    aiBusy = true;
    const [black, white] = counts();
    updateStatus(`AI思考中... | くろ:${black} - しろ:${white}`);
    await delay(250);

    const moves = validMovesOn(board, currentTurn);
    let move = null;
    if (moves.length) {
      if (level === 'random') move = moves[Math.floor(Math.random() * moves.length)];
      else if (level === 'greedy') {
        move = moves.reduce((best, m) =>
          countFlipsOn(board, m[0], m[1], currentTurn) > countFlipsOn(board, best[0], best[1], currentTurn) ? m : best
        );
      } else {
        move = bestMove(board, currentTurn, 3);
      }
    }

    aiBusy = false;
    if (move) await makeMove(move[0], move[1]);
    else {
      currentTurn = opponent(currentTurn);
      renderBoard();
    }
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function startNewGame() {
  board = newBoard();
  currentTurn = BLACK;
  history = [];
  aiBusy = false;
  renderBoard();
  continueGame();
}

function undo() {
  if (aiBusy || history.length === 0) return;
  const state = history.pop();
  board = state.board;
  currentTurn = state.turn;
  renderBoard();
}

function bindControls() {
  document.getElementById('new-game-btn').addEventListener('click', startNewGame);
  document.getElementById('undo-btn').addEventListener('click', undo);
  document.getElementById('hint-black').addEventListener('change', renderBoard);
  document.getElementById('hint-white').addEventListener('change', renderBoard);
  document.getElementById('player-color').addEventListener('change', continueGame);
  document.getElementById('ai-level').addEventListener('change', continueGame);
}

bindControls();
startNewGame();
