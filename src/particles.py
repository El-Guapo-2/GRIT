"""
GRIT - Particle System
Simple particle effects for dust, death, coins, and landing.
"""

import random
import pygame


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life', 'size', 'gravity')

    def __init__(self, x, y, vx, vy, color, life, size=1, gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        return max(0, min(255, int(255 * self.life / self.max_life)))


class ParticleManager:
    """Manages all particle effects in the game."""

    def __init__(self):
        self.particles = []

    def clear(self):
        self.particles.clear()

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface, cam_x, cam_y):
        for p in self.particles:
            sx = int(p.x - cam_x)
            sy = int(p.y - cam_y)
            if -4 <= sx <= surface.get_width() + 4 and -4 <= sy <= surface.get_height() + 4:
                alpha = p.alpha
                if p.size <= 1:
                    col = (*p.color[:3], alpha)
                    surface.set_at((sx, sy), col)
                else:
                    ps = pygame.Surface((p.size, p.size), pygame.SRCALPHA)
                    ps.fill((*p.color[:3], alpha))
                    surface.blit(ps, (sx, sy))

    # ─── Effect emitters ──────────────────────────────────
    def emit_dust(self, x, y):
        """Small dust puff when running."""
        for _ in range(3):
            self.particles.append(Particle(
                x + random.uniform(-2, 2), y,
                random.uniform(-0.3, 0.3), random.uniform(-0.8, -0.2),
                (160, 155, 145), random.randint(8, 15),
                size=1, gravity=0.02,
            ))

    def emit_land(self, x, y):
        """Dust burst on landing."""
        for _ in range(8):
            self.particles.append(Particle(
                x + random.uniform(-4, 4), y,
                random.uniform(-1.2, 1.2), random.uniform(-1.0, -0.2),
                (140, 135, 128), random.randint(10, 20),
                size=random.choice([1, 1, 2]), gravity=0.05,
            ))

    def emit_death(self, x, y, color=(180, 170, 160)):
        """Character explodes into pixels."""
        for _ in range(30):
            self.particles.append(Particle(
                x + random.uniform(-4, 4), y + random.uniform(-6, 2),
                random.uniform(-2.5, 2.5), random.uniform(-3.0, 0.5),
                color, random.randint(20, 45),
                size=random.choice([1, 2, 2, 3]), gravity=0.12,
            ))

    def emit_coin(self, x, y):
        """Sparkle when collecting a coin."""
        for _ in range(10):
            self.particles.append(Particle(
                x + random.uniform(-3, 3), y + random.uniform(-3, 3),
                random.uniform(-1.5, 1.5), random.uniform(-2.0, -0.5),
                random.choice([(185, 165, 85), (220, 205, 130), (255, 240, 170)]),
                random.randint(12, 25),
                size=1, gravity=0.04,
            ))

    def emit_wall_slide(self, x, y):
        """Small particles when wall-sliding."""
        self.particles.append(Particle(
            x + random.uniform(-1, 1), y + random.uniform(-2, 2),
            random.uniform(-0.3, 0.3), random.uniform(-0.5, 0.3),
            (130, 125, 120), random.randint(5, 10),
            size=1, gravity=0.02,
        ))

    def emit_dash(self, x, y, facing_right):
        """Trail particles during dash."""
        for _ in range(4):
            dx = -2 if facing_right else 2
            self.particles.append(Particle(
                x + random.uniform(-2, 2), y + random.uniform(-5, 5),
                dx + random.uniform(-0.5, 0.5), random.uniform(-0.3, 0.3),
                (140, 135, 155), random.randint(6, 12),
                size=random.choice([1, 2]), gravity=0.0,
            ))

    def emit_exit_sparkle(self, x, y, h):
        """Ambient sparkles around exit portal."""
        if random.random() < 0.3:
            self.particles.append(Particle(
                x + random.uniform(-2, 8), y + random.uniform(0, h),
                random.uniform(-0.2, 0.2), random.uniform(-0.6, -0.1),
                random.choice([(155, 150, 165), (180, 175, 195), (200, 195, 210)]),
                random.randint(15, 30),
                size=1, gravity=-0.01,
            ))
