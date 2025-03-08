import { Position, Apple, Wall, Direction, AppleType, GameState } from './types';

class ChaosSnake {
    private readonly gridSize: number = 20;
    private snake: Position[] = [{ x: 10, y: 10 }];
    private apple: Apple = this.createApple();
    private direction: Direction = Direction.Right;
    private nextDirection: Direction = Direction.Right;
    private walls: Wall[] = [];
    private applesEaten: number = 0;
    private cellSize: number = 20;
    private gameState: GameState = GameState.Playing;
    private score: number = 0;

    constructor(
        private canvas: HTMLCanvasElement,
        private ctx: CanvasRenderingContext2D,
        private messageElement: HTMLElement
    ) {
        canvas.width = this.gridSize * this.cellSize;
        canvas.height = this.gridSize * this.cellSize;
        this.setupControls();
    }

    private setupControls(): void {
        document.addEventListener('keydown', (e: KeyboardEvent) => {
            switch(e.key) {
                case 'ArrowUp':
                    if (this.direction !== Direction.Down) this.nextDirection = Direction.Up;
                    break;
                case 'ArrowDown':
                    if (this.direction !== Direction.Up) this.nextDirection = Direction.Down;
                    break;
                case 'ArrowLeft':
                    if (this.direction !== Direction.Right) this.nextDirection = Direction.Left;
                    break;
                case 'ArrowRight':
                    if (this.direction !== Direction.Left) this.nextDirection = Direction.Right;
                    break;
            }
        });
    }

    private createApple(): Apple {
        return {
            x: this.randCoord(),
            y: this.randCoord(),
            type: Math.random() < 0.2 ? AppleType.Bomb : AppleType.Normal
        };
    }

    private randCoord(): number {
        return Math.floor(Math.random() * this.gridSize);
    }

    private showMessage(text: string): void {
        this.messageElement.style.opacity = '1';
        this.messageElement.textContent = text;
        setTimeout(() => {
            this.messageElement.style.opacity = '0';
        }, 1500);
    }

    private checkCollisions(): boolean {
        const head = this.snake[0];
        
        // Wall collision
        if (head.x < 0 || head.x >= this.gridSize || head.y < 0 || head.y >= this.gridSize) {
            return true;
        }

        // Self collision
        for (let i = 1; i < this.snake.length; i++) {
            if (head.x === this.snake[i].x && head.y === this.snake[i].y) {
                return true;
            }
        }

        // Wall collision
        return this.walls.some(wall => wall.x === head.x && wall.y === head.y);
    }

    private checkApple(): void {
        const head = this.snake[0];
        if (head.x === this.apple.x && head.y === this.apple.y) {
            if (this.apple.type === AppleType.Bomb) {
                this.gameState = GameState.GameOver;
                this.showMessage('KABOOM! Madness consumes you...');
                return;
            }

            this.applesEaten++;
            this.score += 100;
            this.snake.push({...this.snake[this.snake.length - 1]});
            this.apple = this.createApple();
            this.triggerMadness();
        }
    }

    private triggerMadness(): void {
        // Teleportation madness
        if (this.applesEaten % 3 === 0 || this.applesEaten % 5 === 0) {
            this.showMessage('Reality warps around you...');
            this.snake[0] = { x: this.randCoord(), y: this.randCoord() };
        }

        // Wall madness
        if (this.applesEaten > 5 && Math.random() < 0.3) {
            this.walls.push({ x: this.randCoord(), y: this.randCoord() });
            this.showMessage('The maze rearranges itself...');
        }

        // Speed madness
        if (this.applesEaten > 10) {
            this.cellSize = 18 + Math.random() * 4;
            this.canvas.style.transform = `scale(${0.9 + Math.random() * 0.2})`;
        }
    }

    private draw(): void {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw snake
        this.snake.forEach((segment, index) => {
            this.ctx.fillStyle = index === 0 ? '#e74c3c' : '#2ecc71';
            this.ctx.fillRect(
                segment.x * this.cellSize,
                segment.y * this.cellSize,
                this.cellSize - 1,
                this.cellSize - 1
            );
        });

        // Draw apple/bomb
        this.ctx.fillStyle = this.apple.type === AppleType.Bomb ? '#f1c40f' : '#c0392b';
        this.ctx.beginPath();
        this.ctx.arc(
            (this.apple.x * this.cellSize) + this.cellSize/2,
            (this.apple.y * this.cellSize) + this.cellSize/2,
            this.cellSize/2 - 1,
            0,
            Math.PI * 2
        );
        this.ctx.fill();

        // Draw walls
        this.ctx.fillStyle = '#7f8c8d';
        this.walls.forEach(wall => {
            this.ctx.fillRect(
                wall.x * this.cellSize,
                wall.y * this.cellSize,
                this.cellSize - 1,
                this.cellSize - 1
            );
        });

        // Draw score
        this.ctx.fillStyle = '#ecf0f1';
        this.ctx.font = '20px Courier New';
        this.ctx.fillText(`Score: ${this.score}`, 10, 30);
    }

    public update(): void {
        if (this.gameState !== GameState.Playing) return;

        this.direction = this.nextDirection;
        const newHead = { ...this.snake[0] };

        switch (this.direction) {
            case Direction.Up: newHead.y--; break;
            case Direction.Down: newHead.y++; break;
            case Direction.Left: newHead.x--; break;
            case Direction.Right: newHead.x++; break;
        }

        this.snake.unshift(newHead);
        this.snake.pop();

        if (this.checkCollisions()) {
            this.gameState = GameState.GameOver;
            this.showMessage('Madness triumphs!');
            return;
        }

        this.checkApple();
        this.draw();
    }
}

// Initialize game
const canvas = document.getElementById('gameCanvas') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const messageElement = document.getElementById('message')!;

const game = new ChaosSnake(canvas, ctx, messageElement);

// Game loop
function gameLoop() {
    game.update();
    requestAnimationFrame(gameLoop);
}

gameLoop();