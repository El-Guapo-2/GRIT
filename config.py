"""
GRIT - Configuration and Constants
All game settings, physics values, and color palettes.
"""

import os
import sys

# ─── Display ───────────────────────────────────────────────
INTERNAL_WIDTH = 480
INTERNAL_HEIGHT = 270
DISPLAY_SCALE = 2
SCREEN_WIDTH = INTERNAL_WIDTH * DISPLAY_SCALE
SCREEN_HEIGHT = INTERNAL_HEIGHT * DISPLAY_SCALE
FPS = 60
GAME_TITLE = "GRIT"

# ─── Tiles ─────────────────────────────────────────────────
TILE = 16  # internal pixel size of one tile

# ─── Physics ───────────────────────────────────────────────
GRAVITY = 0.55
MAX_FALL = 10.0
PLAYER_SPEED = 2.8
PLAYER_ACCEL = 0.45
PLAYER_DECEL = 0.35
JUMP_POWER = -7.2
WALL_SLIDE_SPEED = 1.5
WALL_JUMP_X = 4.0
WALL_JUMP_Y = -6.5
COYOTE_FRAMES = 6
JUMP_BUFFER_FRAMES = 6
DASH_SPEED = 6.0
DASH_FRAMES = 8
DASH_COOLDOWN = 30

# ─── Character palette ────────────────────────────────────
C_SKIN = (210, 180, 150)
C_HAIR = (70, 55, 45)
C_EYE = (35, 30, 25)
C_JACKET = (105, 90, 115)
C_SHIRT = (85, 80, 95)
C_PANTS = (72, 68, 78)
C_BOOTS = (55, 50, 45)

# ─── World palette ────────────────────────────────────────
W_STONE1 = (88, 84, 82)
W_STONE2 = (78, 75, 73)
W_STONE3 = (98, 94, 90)
W_GRASS = (72, 95, 65)
W_GRASS_DARK = (58, 78, 52)
W_DIRT = (100, 80, 60)
W_DIRT_DARK = (82, 65, 48)
W_SPIKE = (145, 62, 52)
W_COIN = (185, 165, 85)
W_COIN_SHINE = (220, 205, 130)
W_EXIT = (155, 150, 165)
W_EXIT_GLOW = (180, 175, 195)
W_BG_FAR = (32, 30, 38)
W_BG_MID = (40, 38, 48)
W_BG_NEAR = (50, 47, 58)
W_PLATFORM = (110, 105, 100)

# ─── UI / Menu palette (monochrome grays) ─────────────────
UI_BG = (22, 22, 24)
UI_TITLE = (210, 210, 215)
UI_TEXT = (150, 150, 155)
UI_TEXT_DIM = (90, 90, 95)
UI_SELECTED = (230, 230, 235)
UI_HIGHLIGHT = (180, 180, 185)
UI_BORDER = (80, 80, 85)
UI_OVERLAY = (0, 0, 0)

# ─── Python splash colors ─────────────────────────────────
PYTHON_BLUE = (55, 105, 155)
PYTHON_YELLOW = (255, 210, 65)

# ─── Audio ─────────────────────────────────────────────────
SAMPLE_RATE = 44100
MASTER_VOLUME = 0.7
MUSIC_VOLUME = 0.4
SFX_VOLUME = 0.6

# ─── Controller mapping (Xbox-style defaults) ─────────────
JOY_JUMP = 0        # A button
JOY_DASH = 2        # X button
JOY_PAUSE = 7       # Start button
JOY_BACK = 1        # B button
JOY_DEADZONE = 0.3

# ─── Level metadata ───────────────────────────────────────
LEVEL_NAMES = [
    "First Steps",
    "The Gap",
    "Vertical Venture",
    "Spike Alley",
    "The Gauntlet",
    "Summit",
]

LEVEL_PAR_TIMES = [25.0, 40.0, 35.0, 50.0, 60.0, 45.0]

# ─── Paths ─────────────────────────────────────────────────
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_data_dir():
    d = os.path.join(get_base_dir(), 'data')
    os.makedirs(d, exist_ok=True)
    return d
