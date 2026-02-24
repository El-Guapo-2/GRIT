"""
GRIT - Player Character
Handles movement physics, animation state, and collision.
"""

import pygame
from config import (
    TILE, GRAVITY, MAX_FALL, PLAYER_SPEED, PLAYER_ACCEL, PLAYER_DECEL,
    JUMP_POWER, WALL_SLIDE_SPEED, WALL_JUMP_X, WALL_JUMP_Y,
    COYOTE_FRAMES, JUMP_BUFFER_FRAMES, DASH_SPEED, DASH_FRAMES, DASH_COOLDOWN,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
)


class Player:
    """The player character with full platformer physics."""

    WIDTH = 8
    HEIGHT = 13

    def __init__(self, x, y, sprites, particles, audio):
        self.sprites = sprites
        self.particles = particles
        self.audio = audio
        # Position (top-left of hitbox)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        # State
        self.on_ground = False
        self.on_wall = 0          # -1 left wall, 1 right wall, 0 none
        self.facing_right = True
        self.alive = True
        # Timers
        self.coyote_timer = 0
        self.jump_buffer = 0
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.dash_dir = 1
        # Animation
        self.anim_state = 'idle'
        self.anim_frame = 0
        self.anim_tick = 0
        self.run_dust_timer = 0
        # Coins collected
        self.coins = 0
        # Respawn
        self.spawn_x = x
        self.spawn_y = y
        self._death_timer = 0

    def handle_input(self, keys):
        """Process input dict: {'left','right','jump','jump_pressed','dash_pressed'}"""
        if not self.alive:
            return

        move_x = 0
        if keys.get('left'):
            move_x = -1
        if keys.get('right'):
            move_x = 1

        # ── Dash ──
        if self.dash_timer > 0:
            self.vx = self.dash_dir * DASH_SPEED
            self.vy = 0
            self.dash_timer -= 1
            return

        # ── Horizontal movement ──
        if move_x != 0:
            self.vx += move_x * PLAYER_ACCEL
            max_spd = PLAYER_SPEED
            self.vx = max(-max_spd, min(max_spd, self.vx))
            self.facing_right = move_x > 0
        else:
            # Decelerate
            if abs(self.vx) < PLAYER_DECEL:
                self.vx = 0
            else:
                self.vx -= PLAYER_DECEL * (1 if self.vx > 0 else -1)

        # ── Jump buffer ──
        if keys.get('jump_pressed'):
            self.jump_buffer = JUMP_BUFFER_FRAMES

        # ── Jumping ──
        if self.jump_buffer > 0:
            if self.coyote_timer > 0:
                # Normal jump
                self.vy = JUMP_POWER
                self.coyote_timer = 0
                self.jump_buffer = 0
                self.on_ground = False
                self.audio.play_sfx('jump')
            elif self.on_wall != 0:
                # Wall jump
                self.vy = WALL_JUMP_Y
                self.vx = -self.on_wall * WALL_JUMP_X
                self.facing_right = self.on_wall < 0
                self.on_wall = 0
                self.jump_buffer = 0
                self.audio.play_sfx('jump')

        # ── Variable jump height ──
        if not keys.get('jump') and self.vy < JUMP_POWER * 0.4:
            self.vy = max(self.vy, JUMP_POWER * 0.4)

        # ── Dash ──
        if keys.get('dash_pressed') and self.dash_cooldown <= 0:
            self.dash_timer = DASH_FRAMES
            self.dash_cooldown = DASH_COOLDOWN
            self.dash_dir = 1 if self.facing_right else -1
            self.audio.play_sfx('dash')

    def update(self, level):
        """Update physics, collision, animation."""
        if not self.alive:
            self._death_timer -= 1
            return self._death_timer <= 0  # Returns True when ready to respawn

        # ── Gravity ──
        if self.dash_timer <= 0:
            if self.on_wall != 0 and self.vy > 0:
                # Wall slide
                self.vy = min(self.vy + GRAVITY * 0.3, WALL_SLIDE_SPEED)
                if self.anim_tick % 3 == 0:
                    wx = self.x if self.on_wall < 0 else self.x + self.WIDTH
                    self.particles.emit_wall_slide(wx, self.y + self.HEIGHT // 2)
            else:
                self.vy = min(self.vy + GRAVITY, MAX_FALL)

        # ── Timers ──
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
        if self.coyote_timer > 0:
            self.coyote_timer -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        # ── Dash particles ──
        if self.dash_timer > 0:
            self.particles.emit_dash(
                self.x + self.WIDTH / 2,
                self.y + self.HEIGHT / 2,
                self.facing_right
            )

        # ── Move and collide ──
        was_on_ground = self.on_ground
        self._move_and_collide(level)

        # ── Landing ──
        if self.on_ground and not was_on_ground and self.vy >= 0:
            self.audio.play_sfx('land')
            self.particles.emit_land(self.x + self.WIDTH / 2, self.y + self.HEIGHT)

        # ── Coyote time ──
        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES

        # ── Running dust ──
        if self.on_ground and abs(self.vx) > 1.5:
            self.run_dust_timer += 1
            if self.run_dust_timer >= 6:
                self.run_dust_timer = 0
                self.particles.emit_dust(self.x + self.WIDTH / 2, self.y + self.HEIGHT)

        # ── Check hazards ──
        if self._check_hazards(level):
            self.die()
            return False

        # ── Check coins ──
        self._check_coins(level)

        # ── Check exit ──
        if self._check_exit(level):
            return 'complete'

        # ── Fell off map ──
        if self.y > level.pixel_height + 32:
            self.die()
            return False

        # ── Animation ──
        self._update_animation()
        self.anim_tick += 1

        return False

    def _move_and_collide(self, level):
        """Move with collision detection against solid tiles."""
        # Horizontal
        self.x += self.vx
        self._collide_h(level)

        # Vertical
        self.y += self.vy
        self._collide_v(level)

        # Wall detection
        self.on_wall = 0
        if not self.on_ground:
            # Check left wall
            if self._tile_solid(level, self.x - 1, self.y + 2) or \
               self._tile_solid(level, self.x - 1, self.y + self.HEIGHT - 2):
                self.on_wall = -1
            # Check right wall
            elif self._tile_solid(level, self.x + self.WIDTH + 1, self.y + 2) or \
                 self._tile_solid(level, self.x + self.WIDTH + 1, self.y + self.HEIGHT - 2):
                self.on_wall = 1

        # Moving platforms
        for plat in level.moving_platforms:
            if self._rect_overlap(
                self.x, self.y + self.HEIGHT - 1, self.WIDTH, 4,
                plat['x'], plat['y'], plat['w'], plat['h']
            ):
                if self.vy >= 0:
                    self.y = plat['y'] - self.HEIGHT
                    self.vy = 0
                    self.on_ground = True
                    self.x += plat.get('dx', 0)

    def _collide_h(self, level):
        """Resolve horizontal collisions."""
        left_tile = int(self.x) // TILE
        right_tile = int(self.x + self.WIDTH - 1) // TILE
        top_tile = int(self.y + 1) // TILE
        bot_tile = int(self.y + self.HEIGHT - 1) // TILE

        for ty in range(top_tile, bot_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                if level.is_solid(tx, ty):
                    if self.vx > 0:
                        self.x = tx * TILE - self.WIDTH
                        self.vx = 0
                    elif self.vx < 0:
                        self.x = (tx + 1) * TILE
                        self.vx = 0

    def _collide_v(self, level):
        """Resolve vertical collisions."""
        self.on_ground = False

        left_tile = int(self.x + 1) // TILE
        right_tile = int(self.x + self.WIDTH - 2) // TILE
        top_tile = int(self.y) // TILE
        bot_tile = int(self.y + self.HEIGHT - 1) // TILE

        for ty in range(top_tile, bot_tile + 1):
            for tx in range(left_tile, right_tile + 1):
                is_platform = level.is_platform(tx, ty)
                is_solid = level.is_solid(tx, ty)

                if is_platform:
                    # One-way: only collide from above
                    if self.vy > 0 and self.y + self.HEIGHT - self.vy <= ty * TILE + 2:
                        self.y = ty * TILE - self.HEIGHT
                        self.vy = 0
                        self.on_ground = True
                elif is_solid:
                    if self.vy > 0:
                        self.y = ty * TILE - self.HEIGHT
                        self.vy = 0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.y = (ty + 1) * TILE
                        self.vy = 0

        # Ground-snap: if not on ground but very close to a solid tile below, snap
        if not self.on_ground and self.vy >= 0 and self.vy < 2.0:
            foot_y = int(self.y + self.HEIGHT)
            tile_y = foot_y // TILE
            snap_y = tile_y * TILE - self.HEIGHT
            if 0 <= self.y - snap_y < 2:
                for tx in range(left_tile, right_tile + 1):
                    if level.is_solid(tx, tile_y):
                        self.y = snap_y
                        self.vy = 0
                        self.on_ground = True
                        break

    def _tile_solid(self, level, px, py):
        tx = int(px) // TILE
        ty = int(py) // TILE
        return level.is_solid(tx, ty)

    def _rect_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2

    def _check_hazards(self, level):
        """Check if player touches any hazard tiles."""
        cx = int(self.x + self.WIDTH / 2) // TILE
        cy_top = int(self.y + 2) // TILE
        cy_bot = int(self.y + self.HEIGHT - 1) // TILE
        left = int(self.x + 2) // TILE
        right = int(self.x + self.WIDTH - 2) // TILE

        for ty in range(cy_top, cy_bot + 1):
            for tx in range(left, right + 1):
                if level.is_hazard(tx, ty):
                    return True
        return False

    def _check_coins(self, level):
        """Collect coins the player overlaps."""
        cx = self.x + self.WIDTH / 2
        cy = self.y + self.HEIGHT / 2
        for coin in level.coins[:]:
            dx = cx - (coin[0] * TILE + TILE / 2)
            dy = cy - (coin[1] * TILE + TILE / 2)
            if abs(dx) < TILE * 0.7 and abs(dy) < TILE * 0.7:
                level.coins.remove(coin)
                self.coins += 1
                self.audio.play_sfx('coin')
                self.particles.emit_coin(
                    coin[0] * TILE + TILE / 2,
                    coin[1] * TILE + TILE / 2
                )

    def _check_exit(self, level):
        """Check if player reached the exit."""
        if level.exit_pos is None:
            return False
        ex, ey = level.exit_pos
        epx, epy = ex * TILE, (ey - 1) * TILE
        cx = self.x + self.WIDTH / 2
        cy = self.y + self.HEIGHT / 2
        return abs(cx - (epx + TILE / 2)) < TILE and abs(cy - (epy + TILE)) < TILE * 1.5

    def die(self):
        if not self.alive:
            return
        self.alive = False
        self._death_timer = 40
        self.audio.play_sfx('death')
        self.particles.emit_death(self.x + self.WIDTH / 2, self.y + self.HEIGHT / 2)

    def respawn(self):
        self.x = float(self.spawn_x)
        self.y = float(self.spawn_y)
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.on_wall = 0
        self.alive = True
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.facing_right = True
        self.anim_state = 'idle'
        self.anim_frame = 0

    def _update_animation(self):
        if self.dash_timer > 0:
            self.anim_state = 'dash'
            return

        if not self.on_ground:
            if self.on_wall != 0:
                new_state = 'wall_slide'
            elif self.vy < 0:
                new_state = 'jump'
            else:
                new_state = 'fall'
        elif abs(self.vx) > 0.5:
            new_state = 'run'
        else:
            new_state = 'idle'

        if new_state != self.anim_state:
            self.anim_state = new_state
            self.anim_frame = 0
            self.anim_tick = 0

        # Advance frame
        speeds = {'idle': 30, 'run': 6, 'jump': 1, 'fall': 1, 'wall_slide': 1, 'dash': 1}
        spd = speeds.get(self.anim_state, 10)
        if self.anim_tick % spd == 0:
            self.anim_frame += 1

    def draw(self, surface, cam_x, cam_y):
        if not self.alive:
            return
        frame = self.sprites.get_frame(self.anim_state, self.anim_frame, self.facing_right)
        fw, fh = frame.get_size()
        # Center the sprite on the hitbox
        draw_x = int(self.x - cam_x) - (fw - self.WIDTH) // 2
        draw_y = int(self.y - cam_y) - (fh - self.HEIGHT)
        surface.blit(frame, (draw_x, draw_y))

    @property
    def center_x(self):
        return self.x + self.WIDTH / 2

    @property
    def center_y(self):
        return self.y + self.HEIGHT / 2
