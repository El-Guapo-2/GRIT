"""
GRIT - Level System
Level data, tile management, camera, and moving platforms.
"""

import pygame
from config import (
    TILE, INTERNAL_WIDTH, INTERNAL_HEIGHT,
    W_BG_FAR, W_BG_MID, W_BG_NEAR, LEVEL_NAMES,
)

# ─── Level Map Legend ──────────────────────────────────────
# '#' = stone (solid)
# 'G' = grass top (solid)
# 'D' = dirt (solid)
# 'S' = player start
# 'E' = exit
# '^' = spikes (hazard)
# 'C' = coin
# '-' = one-way platform
# '=' = moving platform marker (horizontal)
# '|' = moving platform marker (vertical)
# '.' = air

LEVELS = [
    # ── Level 1: First Steps ──────────────────────────────
    [
        "............................................................................",
        "............................................................................",
        "............................................................................",
        "............................................................................",
        "..........................................................C.................",
        "........C...............C.................C............------..........E.....",
        "......------........--------..........-------.........................GG....",
        "..S..............................................................................",
        "..GG......................................................................GG....",
        "..DD..........GGG.......GGG........GGGG.......GGG......GGG..........GGGGGGDD....",
        "..DD..........DDD.......DDD........DDDD.......DDD......DDD..........DDDDDDDD....",
        "..DD..........DDD.......DDD........DDDD.......DDD......DDD..........DDDDDDDD....",
        "############################################################################",
    ],
    # ── Level 2: The Gap ──────────────────────────────────
    [
        "....................................................................................",
        "....................................................................................",
        "....................................................................................",
        "..............C..........C...........C...................C...........................",
        "...........----- .......------.....------..............-----.........C...............",
        "..S.....................................................................................E..",
        "..GG.......................................................GGG....................GGGGG..",
        "..DD..........GGG...............................GGGG.......DDD.......GGG..........DDDDD..",
        "..DD..........DDD........GGG.....GGG............DDDD.......DDD.......DDD..........DDDDD..",
        "..DD..........DDD........DDD.....DDD...^^.......DDDD.......DDD.......DDD..........DDDDD..",
        "..DD..........DDD........DDD.....DDD..^^^^......DDDD.......DDD.......DDD..........DDDDD..",
        "###################^^########^^########^^^########################################",
        "####################^^######^^##########^^^########################################",
    ],
    # ── Level 3: Vertical Venture ─────────────────────────
    [
        "............................",
        "..............E.............",
        "..............GG............",
        "..............DD............",
        ".......GGG..................",
        ".......DDD.........C........",
        "....................GG......",
        "..........C.........DD......",
        "......GGG...................",
        "......DDD.........GGG......",
        "...................DDD......",
        "...GGG......................",
        "...DDD..........C..........",
        "..............GGG..........",
        "..............DDD..........",
        "...C......................",
        "..GGG..................GGG.",
        "..DDD..................DDD.",
        ".......................DDD.",
        "..........GGG.........DDD.",
        "..........DDD.........DDD.",
        "..S.......................",
        "..GG.........GGG.........",
        "..DD.........DDD.........",
        "############################",
    ],
    # ── Level 4: Spike Alley ──────────────────────────────
    [
        "...........................................................................................",
        "...........................................................................................",
        "...........................................................................................",
        "..........C............C............C.............C.............C..........................",
        "..S......-----.......------.......------.......------.......------..........E...............",
        "..GG...........................................................................GGGGGGGGG..",
        "..DD...........GGG..........GGG..........GGG..........GGG..........GGG......DDDDDDDDD..",
        "..DD...........DDD..........DDD..........DDD..........DDD..........DDD......DDDDDDDDD..",
        "..DD...^^.....^^DDD..^^....^^DDD..^^....^^DDD..^^....^^DDD..^^....^^DDD.....DDDDDDDDD..",
        "..DD..^^^^...^^^^DDD^^^^..^^^^DDD^^^^..^^^^DDD^^^^..^^^^DDD^^^^..^^^^DDD....DDDDDDDDD..",
        "#########^^##########^^##########^^##########^^##########^^########################",
        "##########^^##########^^##########^^##########^^##########^^########################",
    ],
    # ── Level 5: The Gauntlet ─────────────────────────────
    [
        "...............................................................................................",
        "...............................................................................................",
        "...............................................................................................",
        "..........C.........C............C............C..............C................C................",
        "..S.....-----....-------.....-------.....-------.......-------.....------...........E.........",
        "..GG..............................................................GGG............GGGGGGG....",
        "..DD........GGG..........GGG..........GGG..........GGG..........DDD............DDDDDDD....",
        "..DD........DDD..........DDD..........DDD..........DDD..........DDD..GGG.......DDDDDDD....",
        "..DD..^^...^^DDD...^^...^^DDD...^^...^^DDD...^^...^^DDD...^^...^^DDD..DDD..^^..DDDDDDD....",
        "..DD.^^^^.^^^^DDD.^^^^.^^^^DDD.^^^^.^^^^DDD.^^^^.^^^^DDD.^^^^.^^^^DDD..DDD.^^^^.DDDDDDD....",
        "########^^#########^^#########^^#########^^#########^^##########^^######^^#############",
        "#########^^#########^^#########^^#########^^#########^^##########^^######^^#############",
        "##############################################################################################",
    ],
    # ── Level 6: Summit ───────────────────────────────────
    [
        "..............................",
        "..............E...............",
        "..............GG..............",
        "..............DD..............",
        "........C.....................",
        ".......GGG.............C.....",
        ".......DDD...........GGG....",
        ".....................DDD....",
        "...C..........................",
        "..GGG.............GGG........",
        "..DDD.............DDD........",
        "....................C.........",
        ".............GGG.............",
        ".............DDD.............",
        "......C......................",
        ".....GGG............GGG.....",
        ".....DDD............DDD.....",
        "............................",
        "..........C.GGG.............",
        "..........GDDDD.............",
        "..........DDDD..............",
        "...GGG......................",
        "...DDD.............GGG.....",
        "....................DDD.....",
        "..S..............C.........",
        "..GG............GGG........",
        "..DD............DDD........",
        "..DD............DDD........",
        "##############################",
    ],
]


class Level:
    """Represents a loaded, playable level."""

    def __init__(self, level_index, tile_sprites):
        self.index = level_index
        self.name = LEVEL_NAMES[level_index] if level_index < len(LEVEL_NAMES) else f"Level {level_index+1}"
        self.tile_sprites = tile_sprites
        self.grid = []
        self.coins = []
        self.start_pos = (2 * TILE, 2 * TILE)
        self.exit_pos = None
        self.moving_platforms = []
        self.width = 0
        self.height = 0
        self.pixel_width = 0
        self.pixel_height = 0
        self._parse(LEVELS[level_index])

    def _parse(self, data):
        """Parse level string data into tile grid."""
        self.height = len(data)
        self.width = max(len(row) for row in data)
        self.pixel_width = self.width * TILE
        self.pixel_height = self.height * TILE

        self.grid = []
        for y, row in enumerate(data):
            grid_row = []
            for x, ch in enumerate(row):
                tile = '.'
                if ch == '#':
                    tile = '#'
                elif ch == 'G':
                    tile = 'G'
                elif ch == 'D':
                    tile = 'D'
                elif ch == '^':
                    tile = '^'
                elif ch == '-':
                    tile = '-'
                elif ch == 'S':
                    self.start_pos = (x * TILE, y * TILE)
                    tile = '.'
                elif ch == 'E':
                    self.exit_pos = (x, y)
                    tile = '.'
                elif ch == 'C':
                    self.coins.append((x, y))
                    tile = '.'
                elif ch == '=' or ch == '|':
                    self.moving_platforms.append({
                        'x': float(x * TILE), 'y': float(y * TILE),
                        'w': TILE * 2, 'h': 5,
                        'sx': float(x * TILE), 'sy': float(y * TILE),
                        'dir': 'h' if ch == '=' else 'v',
                        'range': TILE * 4, 'speed': 0.8,
                        'phase': 0.0, 'dx': 0.0,
                    })
                    tile = '.'
                else:
                    tile = '.'
                grid_row.append(tile)
            # Pad row to width
            while len(grid_row) < self.width:
                grid_row.append('.')
            self.grid.append(grid_row)

    def is_solid(self, tx, ty):
        if tx < 0 or ty < 0 or ty >= self.height or tx >= self.width:
            return tx < 0 or tx >= self.width  # Side walls are solid
        return self.grid[ty][tx] in ('#', 'G', 'D')

    def is_platform(self, tx, ty):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.grid[ty][tx] == '-'
        return False

    def is_hazard(self, tx, ty):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            return self.grid[ty][tx] == '^'
        return False

    def update(self):
        """Update moving platforms."""
        import math
        for plat in self.moving_platforms:
            plat['phase'] += plat['speed'] * 0.02
            old_x = plat['x']
            if plat['dir'] == 'h':
                plat['x'] = plat['sx'] + math.sin(plat['phase']) * plat['range']
                plat['dx'] = plat['x'] - old_x
            else:
                plat['y'] = plat['sy'] + math.sin(plat['phase']) * plat['range']
                plat['dx'] = 0

    def draw(self, surface, cam_x, cam_y, tick):
        """Draw all visible tiles."""
        ts = self.tile_sprites
        start_tx = max(0, int(cam_x) // TILE - 1)
        end_tx = min(self.width, int(cam_x + INTERNAL_WIDTH) // TILE + 2)
        start_ty = max(0, int(cam_y) // TILE - 1)
        end_ty = min(self.height, int(cam_y + INTERNAL_HEIGHT) // TILE + 2)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = self.grid[ty][tx]
                sx = tx * TILE - int(cam_x)
                sy = ty * TILE - int(cam_y)

                if tile == '#':
                    surface.blit(ts.get_stone(tx, ty), (sx, sy))
                elif tile == 'G':
                    surface.blit(ts.grass, (sx, sy))
                elif tile == 'D':
                    surface.blit(ts.dirt, (sx, sy))
                elif tile == '^':
                    surface.blit(ts.spike, (sx, sy))
                elif tile == '-':
                    surface.blit(ts.platform, (sx, sy))

        # Coins
        coin_frame = ts.get_coin_frame(tick)
        for cx, cy in self.coins:
            sx = cx * TILE - int(cam_x)
            sy = cy * TILE - int(cam_y)
            if -TILE <= sx <= INTERNAL_WIDTH + TILE and -TILE <= sy <= INTERNAL_HEIGHT + TILE:
                surface.blit(coin_frame, (sx, sy))

        # Exit
        if self.exit_pos:
            ex, ey = self.exit_pos
            sx = ex * TILE - int(cam_x)
            sy = (ey - 1) * TILE - int(cam_y)
            if -TILE * 2 <= sx <= INTERNAL_WIDTH + TILE * 2:
                surface.blit(ts.exit_tile, (sx, sy))

        # Moving platforms
        for plat in self.moving_platforms:
            sx = int(plat['x'] - cam_x)
            sy = int(plat['y'] - cam_y)
            if -TILE * 3 <= sx <= INTERNAL_WIDTH + TILE * 2:
                surface.blit(ts.moving_platform, (sx, sy))

    def draw_background(self, surface, cam_x, cam_y):
        """Draw parallax background layers."""
        surface.fill(W_BG_FAR)

        # Far layer - large rectangles
        parallax_far = 0.1
        for i in range(0, self.pixel_width + 200, 80):
            x = int(i - cam_x * parallax_far) % (INTERNAL_WIDTH + 200) - 100
            h = 30 + (i * 7) % 40
            y = INTERNAL_HEIGHT - h - 20 - (i * 3) % 30
            pygame.draw.rect(surface, W_BG_MID, (x, y, 40 + (i * 11) % 30, h))

        # Near layer
        parallax_near = 0.3
        for i in range(0, self.pixel_width + 200, 60):
            x = int(i - cam_x * parallax_near) % (INTERNAL_WIDTH + 160) - 80
            h = 20 + (i * 11) % 35
            y = INTERNAL_HEIGHT - h - 5 - (i * 7) % 20
            pygame.draw.rect(surface, W_BG_NEAR, (x, y, 25 + (i * 3) % 20, h))


class Camera:
    """Smooth-follow camera."""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

    def update(self, target_x, target_y, level):
        """Smoothly follow target, clamped to level bounds."""
        self.target_x = target_x - INTERNAL_WIDTH / 2
        self.target_y = target_y - INTERNAL_HEIGHT / 2

        # Clamp to level bounds
        max_x = max(0, level.pixel_width - INTERNAL_WIDTH)
        max_y = max(0, level.pixel_height - INTERNAL_HEIGHT)
        self.target_x = max(0, min(self.target_x, max_x))
        self.target_y = max(0, min(self.target_y, max_y))

        # Smooth follow
        lerp = 0.12
        self.x += (self.target_x - self.x) * lerp
        self.y += (self.target_y - self.y) * lerp

    def snap(self, target_x, target_y, level):
        """Instantly snap camera to target."""
        self.target_x = target_x - INTERNAL_WIDTH / 2
        self.target_y = target_y - INTERNAL_HEIGHT / 2
        max_x = max(0, level.pixel_width - INTERNAL_WIDTH)
        max_y = max(0, level.pixel_height - INTERNAL_HEIGHT)
        self.x = max(0, min(self.target_x, max_x))
        self.y = max(0, min(self.target_y, max_y))
        self.target_x = self.x
        self.target_y = self.y
