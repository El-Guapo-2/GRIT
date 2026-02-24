# GRIT

**Keep Moving. Keep Climbing. Stay Gritty.**

A retro 8-bit platformer built entirely in Python.

*Created by Noah Crandall in cooperation with Anthropic Claude*

---

## About

GRIT is a fast-paced retro platformer with tight controls, hand-crafted levels, and an
arcade mode with leaderboards. Race through 6 challenging levels, master wall-jumps and
dashes, and compete for the best times.

## Features

- **Story Mode** – Play through 6 levels of increasing difficulty
- **Arcade Mode** – Speedrun any unlocked level with leaderboard tracking
- **Tight Controls** – Run, jump, wall-jump, and dash with responsive physics
- **Chiptune Audio** – Procedurally generated music and sound effects
- **Controller Support** – Xbox, PlayStation, and generic controllers
- **Retro Aesthetic** – Authentic 8-bit pixel art with a muted color palette

## Controls

| Action       | Keyboard         | Controller       |
|-------------|------------------|------------------|
| Move        | Arrow Keys / WASD | Left Stick / D-pad |
| Jump        | Z / Space        | A / Cross        |
| Dash        | X                | X / Square       |
| Pause       | Escape           | Start            |
| Back (menu) | Escape           | B / Circle       |
| Select      | Enter / Space    | A / Cross        |
| Fullscreen  | F11              | –                |

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Requirements

- Python 3.8+
- pygame >= 2.5.0
- numpy >= 1.24.0

## Packaging for Distribution

```bash
# Using PyInstaller (recommended)
pip install pyinstaller
pyinstaller --onefile --windowed --name GRIT main.py

# The executable will be in the dist/ folder
```

## Project Structure

```
├── main.py              # Entry point
├── config.py            # Game settings and constants
├── setup.py             # Packaging configuration
├── requirements.txt     # Python dependencies
├── src/
│   ├── engine.py        # Main game loop and state machine
│   ├── player.py        # Player physics and animation
│   ├── level.py         # Level data, tiles, and camera
│   ├── sprites.py       # Pixel art sprite generation
│   ├── audio.py         # Music and sound effect generation
│   ├── particles.py     # Particle effects system
│   ├── menu.py          # All menu screens and HUD
│   └── leaderboard.py   # Time tracking and persistence
└── data/                # Auto-created for save data
    ├── leaderboard.json
    └── progress.json
```

## License

MIT License
