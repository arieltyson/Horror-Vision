type Position = { x: number; y: number };
type Apple = Position & { type: AppleType };
type Wall = Position;

enum Direction { 
    Up = 'Up',
    Down = 'Down',
    Left = 'Left',
    Right = 'Right'
}

enum AppleType { 
    Normal = 'Normal',
    Bomb = 'Bomb'
}

enum GameState {
    Playing,
    GameOver
}

export { Position, Apple, Wall, Direction, AppleType, GameState };