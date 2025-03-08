// game.js
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const gridSize = 20; // size of each grid cell in pixels
const canvasSize = canvas.width; // assuming a square canvas (600x600)
const totalCells = canvasSize / gridSize; // e.g. 600/20 = 30 cells per row

// The snake’s state
let snake = {
  x: Math.floor(totalCells / 2),
  y: Math.floor(totalCells / 2),
  dx: 1,  // initial movement to the right (1 cell per update)
  dy: 0,
  cells: [],
  maxCells: 4
};

let score = 0;
let applesEaten = 0;
let food = randomFood();
let obstacles = [];
let trap = false; // if true, the current food is a dangerous trap
let gameOver = false;
let lastTime = 0;
const speed = 8; // moves per second

// --- Utility Functions ---
function randomFood() {
  const cell = {
    x: Math.floor(Math.random() * totalCells),
    y: Math.floor(Math.random() * totalCells)
  };
  // Ensure food doesn't spawn on snake or on an obstacle.
  if (snake.cells.some(c => c.x === cell.x && c.y === cell.y)) {
    return randomFood();
  }
  if (obstacles.some(o => o.x === cell.x && o.y === cell.y)) {
    return randomFood();
  }
  return cell;
}

function randomObstacle() {
  const cell = {
    x: Math.floor(Math.random() * totalCells),
    y: Math.floor(Math.random() * totalCells)
  };
  // Avoid spawning on the snake or the food.
  if (snake.x === cell.x && snake.y === cell.y) return randomObstacle();
  if (food.x === cell.x && food.y === cell.y) return randomObstacle();
  if (snake.cells.some(c => c.x === cell.x && c.y === cell.y)) {
    return randomObstacle();
  }
  return cell;
}

// --- Drawing Function ---
function draw() {
  // Clear the canvas
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvasSize, canvasSize);

  // Draw the food (or trap)
  if (trap) {
    ctx.fillStyle = "red";
  } else {
    ctx.fillStyle = "lime";
  }
  ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize, gridSize);

  // Draw obstacles
  ctx.fillStyle = "gray";
  obstacles.forEach(obs => {
    ctx.fillRect(obs.x * gridSize, obs.y * gridSize, gridSize, gridSize);
  });

  // Draw the snake
  ctx.fillStyle = "white";
  snake.cells.forEach(cell => {
    ctx.fillRect(cell.x * gridSize, cell.y * gridSize, gridSize - 1, gridSize - 1);
  });

  // Update score display
  document.getElementById("score").innerText = "Score: " + score;
}

// --- Update Function ---
function update(deltaTime) {
  // Only update when enough time has passed for desired speed.
  if (deltaTime < 1000 / speed) return;

  // Move the snake’s head
  snake.x += snake.dx;
  snake.y += snake.dy;

  // Check for boundary collisions (game over if out of bounds)
  if (snake.x < 0 || snake.x >= totalCells || snake.y < 0 || snake.y >= totalCells) {
    endGame();
    return;
  }

  // Check collision with obstacles
  for (const obs of obstacles) {
    if (snake.x === obs.x && snake.y === obs.y) {
      endGame();
      return;
    }
  }

  // Check trap collision (if food is a trap)
  if (trap && snake.x === food.x && snake.y === food.y) {
    endGame();
    return;
  }

  // Update snake body: add new head position
  snake.cells.unshift({ x: snake.x, y: snake.y });
  if (snake.cells.length > snake.maxCells) {
    snake.cells.pop();
  }

  // Self-collision check
  for (let i = 1; i < snake.cells.length; i++) {
    if (snake.x === snake.cells[i].x && snake.y === snake.cells[i].y) {
      endGame();
      return;
    }
  }

  // Check if snake eats food (only if food is not a trap)
  if (!trap && snake.x === food.x && snake.y === food.y) {
    snake.maxCells++;
    score += 10;
    applesEaten++;
    // Respawn food
    food = randomFood();
    // Randomly reset trap state (food becomes normal)
    trap = false;
    // Trigger a madness event based on count
    triggerMadness();
  }

  draw();
}

// --- Madness Event Function ---
function triggerMadness() {
  // Example madness events:
  // 1. Every 3 apples eaten, teleport the snake.
  if (applesEaten % 3 === 0) {
    showMessage("You feel disoriented...");
    setTimeout(() => {
      snake.x = Math.floor(Math.random() * totalCells);
      snake.y = Math.floor(Math.random() * totalCells);
      snake.cells = [{ x: snake.x, y: snake.y }];
      showMessage("Teleported!");
    }, 1000);
  }
  // 2. Every 5 apples eaten, add a new obstacle.
  if (applesEaten % 5 === 0) {
    showMessage("Obstacles arise...");
    setTimeout(() => {
      obstacles.push(randomObstacle());
      showMessage("");
    }, 1000);
  }
  // 3. Random chance to have the food turn into a trap (dangerous instead of edible)
  if (Math.random() < 0.1) {
    trap = true;
    showMessage("The food looks... wrong!");
    setTimeout(() => showMessage(""), 1000);
  }
}

// --- Message Display ---
function showMessage(msg) {
  const msgEl = document.getElementById("message");
  msgEl.innerText = msg;
  msgEl.style.opacity = msg ? "1" : "0";
}

// --- End Game ---
function endGame() {
  gameOver = true;
  showMessage("Game Over!");
}

// --- Input Handling ---
document.addEventListener("keydown", function (e) {
  // Prevent snake from reversing directly
  switch (e.keyCode) {
    case 37: // left arrow
      if (snake.dx !== 1) { snake.dx = -1; snake.dy = 0; }
      break;
    case 38: // up arrow
      if (snake.dy !== 1) { snake.dy = -1; snake.dx = 0; }
      break;
    case 39: // right arrow
      if (snake.dx !== -1) { snake.dx = 1; snake.dy = 0; }
      break;
    case 40: // down arrow
      if (snake.dy !== -1) { snake.dy = 1; snake.dx = 0; }
      break;
    // Optionally support WASD:
    case 65: // A - left
      if (snake.dx !== 1) { snake.dx = -1; snake.dy = 0; }
      break;
    case 87: // W - up
      if (snake.dy !== 1) { snake.dy = -1; snake.dx = 0; }
      break;
    case 68: // D - right
      if (snake.dx !== -1) { snake.dx = 1; snake.dy = 0; }
      break;
    case 83: // S - down
      if (snake.dy !== -1) { snake.dy = 1; snake.dx = 0; }
      break;
  }
});

// --- Game Loop ---
function gameLoop(timestamp) {
  if (gameOver) return; // stop looping if game is over
  if (!lastTime) lastTime = timestamp;
  const deltaTime = timestamp - lastTime;
  if (deltaTime > 1000 / speed) {
    update(deltaTime);
    lastTime = timestamp;
  }
  requestAnimationFrame(gameLoop);
}

// Start the game loop
requestAnimationFrame(gameLoop);