"""
GRIT - Sprite System
Procedurally generates all pixel-art sprites for the character, tiles, and objects.
"""

import pygame
from config import (
    TILE, C_SKIN, C_HAIR, C_EYE, C_JACKET, C_SHIRT, C_PANTS, C_BOOTS,
    W_STONE1, W_STONE2, W_STONE3, W_GRASS, W_GRASS_DARK, W_DIRT, W_DIRT_DARK,
    W_SPIKE, W_COIN, W_COIN_SHINE, W_EXIT, W_EXIT_GLOW, W_PLATFORM,
)

TRANSPARENT = (0, 0, 0, 0)

# ─── Colour key for character frames ──────────────────────
_CK = {
    '.': None,
    'H': C_HAIR,
    'S': C_SKIN,
    'E': C_EYE,
    'J': C_JACKET,
    'T': C_SHIRT,
    'P': C_PANTS,
    'B': C_BOOTS,
}


def _frame_to_surface(rows):
    """Convert a list-of-strings frame to a pygame Surface (1px per char)."""
    h = len(rows)
    w = max(len(r) for r in rows)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(TRANSPARENT)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = _CK.get(ch)
            if col:
                surf.set_at((x, y), (*col, 255))
    return surf


# ─── Character frames (10 wide × 14 tall) ─────────────────
# Each frame is designed at 1px scale; will be scaled to game size.

IDLE_1 = [
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "....SS....",
    "...JJJJ...",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "...JJJJ...",
    "...PPPP...",
    "...PP.PP..",
    "..BB..BB..",
    "..........",
]

IDLE_2 = [
    "..........",
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "....SS....",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "...JJJJ...",
    "...PPPP...",
    "...PP.PP..",
    "..BB..BB..",
    "..........",
]

RUN_1 = [
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "...SSS....",
    "..JJJJJ...",
    "..JTTTTJ..",
    "..JJJJJJ..",
    "...PPPP...",
    "...PP.PP..",
    "..BB...BB.",
    "..........",
    "..........",
]

RUN_2 = [
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "....SS....",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "...JJJJ...",
    "...PPPP...",
    "..PP..PP..",
    "..BB..BB..",
    "..........",
    "..........",
]

RUN_3 = [
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "...SSS....",
    ".JJJJJJ...",
    "..JTTTTJ..",
    "..JJJJJ...",
    "...PPPP...",
    "..PP...PP.",
    ".BB.....BB",
    "..........",
    "..........",
]

RUN_4 = [
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "....SS....",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "...JJJJ...",
    "...PPPP...",
    "....PPPP..",
    "...BB..BB.",
    "..........",
    "..........",
]

JUMP_UP = [
    "..SS..SS..",
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "....SS....",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "...JJJJ...",
    "...PPPP...",
    "...PP.PP..",
    "..BB..BB..",
    "..........",
]

FALL = [
    "..........",
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    ".SS.SS.SS.",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "...JJJJ...",
    "...PPPP...",
    "..PP..PP..",
    ".BB....BB.",
    "..........",
]

WALL_SLIDE = [
    "..........",
    "...HHHH...",
    "..HHHHHH..",
    "..HHSESH..",
    "...SSSSH..",
    "...SSSS...",
    "....SS....",
    "..JJJJJJ..",
    "..JTTTTJ..",
    "..JJJJJJ..",
    "...PPPP...",
    "...PPPP...",
    "...BB.BB..",
    "..........",
]

DASH_FRAME = [
    "..........",
    "...HHHH...",
    "..HHHHHH..",
    "..HSESHH..",
    "..HSSSS...",
    "...SSSS...",
    "SS..SS..SS",
    ".JJJJJJJ.",
    "..JTTTTJ..",
    "...JJJJ...",
    "..PPPPPP..",
    "..BB..BB..",
    "..........",
    "..........",
]


class CharacterSprites:
    """Manages all character animation frames."""

    def __init__(self, scale=2):
        self.scale = scale
        self._cache = {}
        self.animations = {
            'idle': [IDLE_1, IDLE_2],
            'run': [RUN_1, RUN_2, RUN_3, RUN_4],
            'jump': [JUMP_UP],
            'fall': [FALL],
            'wall_slide': [WALL_SLIDE],
            'dash': [DASH_FRAME],
        }
        self._build()

    def _build(self):
        for anim_name, frames in self.animations.items():
            surfs = []
            for frame_data in frames:
                base = _frame_to_surface(frame_data)
                w, h = base.get_size()
                scaled = pygame.transform.scale(base, (w * self.scale, h * self.scale))
                surfs.append(scaled)
            self._cache[anim_name] = surfs
            # Flipped versions
            self._cache[anim_name + '_left'] = [
                pygame.transform.flip(s, True, False) for s in surfs
            ]

    def get_frame(self, anim, frame_idx, facing_right=True):
        key = anim if facing_right else anim + '_left'
        frames = self._cache.get(key, self._cache.get('idle'))
        return frames[frame_idx % len(frames)]

    def get_frame_count(self, anim):
        frames = self._cache.get(anim, self._cache.get('idle'))
        return len(frames)


# ─── Tile Sprites ──────────────────────────────────────────
_tile_cache = {}


def _make_stone_tile(variant=0):
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    colors = [W_STONE1, W_STONE2, W_STONE3]
    base = colors[variant % 3]
    s.fill(base)
    # Add subtle texture
    import random
    rng = random.Random(variant * 37)
    for _ in range(6):
        x = rng.randint(0, TILE - 3)
        y = rng.randint(0, TILE - 3)
        shade = tuple(max(0, c + rng.randint(-12, 12)) for c in base)
        pygame.draw.rect(s, shade, (x, y, 2, 2))
    # Edge highlights
    pygame.draw.line(s, tuple(min(255, c + 15) for c in base), (0, 0), (TILE - 1, 0))
    pygame.draw.line(s, tuple(max(0, c - 15) for c in base), (0, TILE - 1), (TILE - 1, TILE - 1))
    return s


def _make_grass_tile():
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    s.fill(W_DIRT)
    # Grass top
    pygame.draw.rect(s, W_GRASS, (0, 0, TILE, 5))
    pygame.draw.rect(s, W_GRASS_DARK, (0, 5, TILE, 2))
    # Grass blades
    for x in range(0, TILE, 3):
        pygame.draw.line(s, W_GRASS, (x, 0), (x, -1))
    return s


def _make_dirt_tile():
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    s.fill(W_DIRT)
    import random
    rng = random.Random(42)
    for _ in range(4):
        x = rng.randint(0, TILE - 3)
        y = rng.randint(0, TILE - 3)
        pygame.draw.rect(s, W_DIRT_DARK, (x, y, 2, 2))
    return s


def _make_spike_tile():
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    s.fill(TRANSPARENT)
    # Three spikes
    spike_w = TILE // 3
    for i in range(3):
        bx = i * spike_w
        points = [(bx, TILE), (bx + spike_w // 2, 2), (bx + spike_w, TILE)]
        pygame.draw.polygon(s, W_SPIKE, points)
        # Highlight
        darker = tuple(max(0, c - 30) for c in W_SPIKE)
        pygame.draw.polygon(s, darker, points, 1)
    return s


def _make_coin_frames():
    """Create 4 coin animation frames."""
    frames = []
    widths = [TILE - 4, TILE - 6, TILE - 10, TILE - 6]
    for w in widths:
        s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        s.fill(TRANSPARENT)
        cx, cy = TILE // 2, TILE // 2
        if w > 2:
            pygame.draw.ellipse(s, W_COIN, (cx - w // 2, cy - (TILE - 4) // 2, w, TILE - 4))
            # Shine
            if w > 4:
                pygame.draw.ellipse(s, W_COIN_SHINE, (cx - w // 4, cy - (TILE - 8) // 2, w // 2, TILE - 8))
        frames.append(s)
    return frames


def _make_exit_tile():
    s = pygame.Surface((TILE, TILE * 2), pygame.SRCALPHA)
    s.fill(TRANSPARENT)
    # Door frame
    pygame.draw.rect(s, W_EXIT, (1, 0, TILE - 2, TILE * 2))
    # Inner glow
    pygame.draw.rect(s, W_EXIT_GLOW, (3, 2, TILE - 6, TILE * 2 - 4))
    # Bright center
    bright = tuple(min(255, c + 30) for c in W_EXIT_GLOW)
    pygame.draw.rect(s, bright, (5, 4, TILE - 10, TILE * 2 - 8))
    return s


def _make_platform_tile():
    s = pygame.Surface((TILE, 4), pygame.SRCALPHA)
    s.fill(TRANSPARENT)
    pygame.draw.rect(s, W_PLATFORM, (0, 0, TILE, 3))
    lighter = tuple(min(255, c + 20) for c in W_PLATFORM)
    pygame.draw.line(s, lighter, (0, 0), (TILE - 1, 0))
    return s


def _make_moving_platform():
    s = pygame.Surface((TILE * 2, 6), pygame.SRCALPHA)
    s.fill(TRANSPARENT)
    pygame.draw.rect(s, W_PLATFORM, (0, 0, TILE * 2, 5))
    lighter = tuple(min(255, c + 25) for c in W_PLATFORM)
    pygame.draw.line(s, lighter, (0, 0), (TILE * 2 - 1, 0))
    darker = tuple(max(0, c - 15) for c in W_PLATFORM)
    pygame.draw.line(s, darker, (0, 4), (TILE * 2 - 1, 4))
    return s


class TileSprites:
    """Manages all tile/world sprites."""

    def __init__(self):
        self.stone = [_make_stone_tile(i) for i in range(3)]
        self.grass = _make_grass_tile()
        self.dirt = _make_dirt_tile()
        self.spike = _make_spike_tile()
        self.coin_frames = _make_coin_frames()
        self.exit_tile = _make_exit_tile()
        self.platform = _make_platform_tile()
        self.moving_platform = _make_moving_platform()

    def get_stone(self, x, y):
        return self.stone[(x * 7 + y * 13) % 3]

    def get_coin_frame(self, tick):
        idx = (tick // 8) % len(self.coin_frames)
        return self.coin_frames[idx]
