"""
GRIT - Menu System v2
All menu screens using 8-bit bitmap font system.
Inspired by clean split-layout menus and grid-based level select.
"""

import pygame
from config import (
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    UI_BG, UI_TITLE, UI_TEXT, UI_TEXT_DIM, UI_SELECTED, UI_HIGHLIGHT,
    UI_BORDER, PYTHON_BLUE, PYTHON_YELLOW, LEVEL_NAMES, LEVEL_PAR_TIMES,
    GAME_TITLE,
)
from src.fonts import PixelFont
from src import leaderboard


# ─── Shared font instances ────────────────────────────────
_font_lg = PixelFont(scale=3)   # Large (titles, "GRIT")
_font_md = PixelFont(scale=2)   # Medium (menu options, headings)
_font_sm = PixelFont(scale=1)   # Small (info text, hints)


def _hline(surface, y, color=UI_BORDER, margin=30):
    """Draw a horizontal divider line."""
    pygame.draw.line(surface, color, (margin, y), (INTERNAL_WIDTH - margin, y))


def _draw_box(surface, x, y, w, h, fill=None, border=UI_BORDER, border_w=1):
    """Draw a rounded-ish box (rectangle with border)."""
    if fill:
        pygame.draw.rect(surface, fill, (x, y, w, h))
    if border:
        pygame.draw.rect(surface, border, (x, y, w, h), border_w)


# ─── Splash Screen ────────────────────────────────────────
class SplashScreen:
    """'Powered by Python' splash that fades in and out."""

    def __init__(self):
        self.timer = 0
        self.duration = 180  # 3 seconds at 60fps
        self.done = False

    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.done = True

    def draw(self, surface):
        surface.fill((0, 0, 0))

        # Calculate alpha for fade in/hold/fade out
        fade_in = 40
        hold_end = self.duration - 50
        fade_out_end = self.duration

        if self.timer < fade_in:
            alpha = self.timer / fade_in
        elif self.timer < hold_end:
            alpha = 1.0
        else:
            alpha = (fade_out_end - self.timer) / (fade_out_end - hold_end)
        alpha = max(0.0, min(1.0, alpha))

        # Create overlay with alpha
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)

        # "Powered by" in small font
        a = int(alpha * 255)
        color_dim = (180, 180, 185, a)
        color_py = (PYTHON_YELLOW[0], PYTHON_YELLOW[1], PYTHON_YELLOW[2], a)

        _font_sm.draw(overlay, "POWERED BY", INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 - 18,
                      color_dim, center=True)

        # "PYTHON" in yellow medium font
        _font_md.draw(overlay, "PYTHON", INTERNAL_WIDTH // 2, INTERNAL_HEIGHT // 2 + 4,
                      color_py, center=True)

        # Python colored accent bar
        bar_w = 50
        bar_x = INTERNAL_WIDTH // 2 - bar_w // 2
        bar_y = INTERNAL_HEIGHT // 2 + 22
        pygame.draw.rect(overlay, (PYTHON_BLUE[0], PYTHON_BLUE[1], PYTHON_BLUE[2], a),
                         (bar_x, bar_y, bar_w // 2, 2))
        pygame.draw.rect(overlay, color_py,
                         (bar_x + bar_w // 2, bar_y, bar_w // 2, 2))

        surface.blit(overlay, (0, 0))


# ─── Main Menu ────────────────────────────────────────────
class MainMenu:
    """Main menu with split layout — options left, credits right."""

    def __init__(self):
        self.options = ["Story Mode", "Arcade Mode", "Settings", "Quit"]
        self.selected = 0
        self.result = None
        self._title_bob = 0
        self._secret_rect = None  # Hitbox for the first 'I' in DETERMINATION
        self.cheat_activated = False  # Engine checks this

    def handle_input(self, keys):
        if keys.get('menu_up'):
            self.selected = (self.selected - 1) % len(self.options)
            return 'move'
        if keys.get('menu_down'):
            self.selected = (self.selected + 1) % len(self.options)
            return 'move'
        if keys.get('menu_select'):
            self.result = self.options[self.selected].lower().replace(' ', '_')
            return 'select'
        return None

    def handle_mouse_click(self, internal_x, internal_y):
        """Check if a click hits the secret 'I'. Returns True if cheat triggered."""
        if self._secret_rect and self._secret_rect.collidepoint(internal_x, internal_y):
            self.cheat_activated = True
            return True
        return False

    def update(self):
        self._title_bob += 1

    def draw(self, surface):
        surface.fill(UI_BG)

        # ── Title "GRIT" at top center ──
        title_y = 40 + (1 if (self._title_bob // 60) % 2 == 0 else 0)
        _font_lg.draw(surface, GAME_TITLE, INTERNAL_WIDTH // 2, title_y,
                      UI_TITLE, center=True, shadow=True, shadow_color=(0, 0, 0))

        # Tagline
        _font_sm.draw(surface, "KEEP MOVING. KEEP CLIMBING.",
                      INTERNAL_WIDTH // 2, title_y + 30,
                      UI_TEXT_DIM, center=True)

        # ── Divider ──
        _hline(surface, 80)

        # ── Split layout: options left, info right ──
        mid_x = INTERNAL_WIDTH // 2
        left_x = 50
        right_x = mid_x + 20

        # Vertical divider
        pygame.draw.line(surface, UI_BORDER,
                         (mid_x - 5, 90), (mid_x - 5, INTERNAL_HEIGHT - 40))

        # ── Left side: Menu options ──
        menu_y = 102
        for i, opt in enumerate(self.options):
            y = menu_y + i * 24
            is_sel = (i == self.selected)
            color = UI_SELECTED if is_sel else UI_TEXT

            if is_sel:
                # Selection highlight box
                _draw_box(surface, left_x - 8, y - 4,
                          mid_x - left_x - 10, 18,
                          fill=(35, 35, 40), border=UI_BORDER)
                _font_md.draw(surface, "> " + opt.upper(), left_x, y, color)
            else:
                _font_md.draw(surface, "  " + opt.upper(), left_x, y, color)

        # ── Right side: Game info / credits ──
        info_y = 100
        _font_sm.draw(surface, "ABOUT", right_x, info_y, UI_HIGHLIGHT)
        _font_sm.draw(surface, "A PRECISION", right_x, info_y + 14, UI_TEXT_DIM)
        _font_sm.draw(surface, "PLATFORMER ABOUT", right_x, info_y + 24, UI_TEXT_DIM)
        _font_sm.draw(surface, "PERSISTENCE AND", right_x, info_y + 34, UI_TEXT_DIM)
        det_rect = _font_sm.draw(surface, "DETERMINATION.", right_x, info_y + 44, UI_TEXT_DIM)
        # The first 'I' is at character index 6 in "DETERMINATION."
        # Each char at scale=1 is 5px wide + 1px spacing = 6px per char
        char_w = 6  # GLYPH_W(5) * scale(1) + spacing(1)
        char_h = 7  # GLYPH_H(7) * scale(1)
        self._secret_rect = pygame.Rect(det_rect.x + 6 * char_w, det_rect.y, char_w, char_h)

        _font_sm.draw(surface, "CREATED BY", right_x, info_y + 66, UI_HIGHLIGHT)
        _font_sm.draw(surface, "NOAH CRANDALL", right_x, info_y + 78, UI_TEXT)
        _font_sm.draw(surface, "IN COOPERATION WITH", right_x, info_y + 90, UI_TEXT_DIM)
        _font_sm.draw(surface, "ANTHROPIC CLAUDE", right_x, info_y + 100, UI_TEXT)

        # ── Controls hint (bottom) ──
        _hline(surface, INTERNAL_HEIGHT - 26)
        _font_sm.draw(surface, "LEFT/RIGHT: MOVE   UP/W: JUMP   SHIFT: DASH   ENTER: SELECT",
                      INTERNAL_WIDTH // 2, INTERNAL_HEIGHT - 14,
                      (55, 55, 60), center=True)


# ─── Level Select ─────────────────────────────────────────
class LevelSelect:
    """Grid-based level selection screen (3 columns × 2 rows)."""

    COLS = 3
    ROWS = 2

    def __init__(self, mode='story', unlocked=1):
        self.mode = mode
        self.selected = 0
        self.unlocked = unlocked
        self.result = None
        self.total = len(LEVEL_NAMES)

    def handle_input(self, keys):
        if keys.get('menu_right'):
            new = self.selected + 1
            if new < self.total:
                self.selected = new
                return 'move'
        if keys.get('menu_left'):
            new = self.selected - 1
            if new >= 0:
                self.selected = new
                return 'move'
        if keys.get('menu_down'):
            new = self.selected + self.COLS
            if new < self.total:
                self.selected = new
                return 'move'
        if keys.get('menu_up'):
            new = self.selected - self.COLS
            if new >= 0:
                self.selected = new
                return 'move'
        if keys.get('menu_select'):
            if self.selected < self.unlocked:
                self.result = self.selected
                return 'select'
        if keys.get('menu_back'):
            self.result = 'back'
            return 'select'
        return None

    def draw(self, surface):
        surface.fill(UI_BG)

        # Header
        title = "STORY MODE" if self.mode == 'story' else "ARCADE MODE"
        _font_md.draw(surface, title, INTERNAL_WIDTH // 2, 18, UI_TITLE, center=True)
        _hline(surface, 34)

        # Grid layout
        grid_w = 120   # cell width
        grid_h = 80    # cell height
        gap_x = 14
        gap_y = 12
        total_grid_w = self.COLS * grid_w + (self.COLS - 1) * gap_x
        start_x = (INTERNAL_WIDTH - total_grid_w) // 2
        start_y = 48

        for i in range(self.total):
            col = i % self.COLS
            row = i // self.COLS

            x = start_x + col * (grid_w + gap_x)
            y = start_y + row * (grid_h + gap_y)

            locked = i >= self.unlocked
            is_sel = (i == self.selected)

            # Cell background
            if is_sel and not locked:
                bg_color = (40, 40, 48)
                border_color = UI_HIGHLIGHT
            elif is_sel and locked:
                bg_color = (30, 30, 35)
                border_color = (60, 60, 65)
            else:
                bg_color = (28, 28, 32)
                border_color = UI_BORDER

            _draw_box(surface, x, y, grid_w, grid_h, fill=bg_color, border=border_color)

            # Level number (big)
            num_str = str(i + 1)
            _font_md.draw(surface, num_str, x + 10, y + 8,
                          UI_HIGHLIGHT if not locked else (50, 50, 55))

            if locked:
                # Lock icon (simple pixel art)
                lx = x + grid_w // 2
                ly = y + grid_h // 2 + 4
                # Lock body
                pygame.draw.rect(surface, (55, 55, 60), (lx - 6, ly, 12, 10))
                # Lock shackle
                pygame.draw.rect(surface, (55, 55, 60), (lx - 4, ly - 5, 8, 6), 1)
                _font_sm.draw(surface, "LOCKED", x + grid_w // 2, y + grid_h - 12,
                              (50, 50, 55), center=True)
            else:
                # Level name
                _font_sm.draw(surface, LEVEL_NAMES[i].upper(), x + 10, y + 28, UI_TEXT)

                # Best time
                best = leaderboard.get_best_time(i)
                time_str = leaderboard.format_time(best) if best is not None else "--:--.--"
                _font_sm.draw(surface, time_str, x + 10, y + 42, UI_TEXT_DIM)

                # Par time
                par_str = "PAR " + leaderboard.format_time(LEVEL_PAR_TIMES[i])
                _font_sm.draw(surface, par_str, x + 10, y + 54, (60, 60, 65))

                # Beat par indicator
                if best is not None and best < LEVEL_PAR_TIMES[i] and best > 0:
                    _font_sm.draw(surface, "*", x + grid_w - 14, y + 8, (120, 170, 110))

        # Footer
        _hline(surface, INTERNAL_HEIGHT - 26)
        _font_sm.draw(surface, "ENTER: PLAY   ESC: BACK",
                      INTERNAL_WIDTH // 2, INTERNAL_HEIGHT - 14,
                      UI_TEXT_DIM, center=True)

        # Back indicator
        _font_sm.draw(surface, "< BACK", 12, INTERNAL_HEIGHT - 14, UI_TEXT_DIM)


# ─── Pause Menu ───────────────────────────────────────────
class PauseMenu:
    """In-game pause overlay."""

    def __init__(self):
        self.options = ["Resume", "Restart Level", "Quit to Menu"]
        self.selected = 0
        self.result = None

    def handle_input(self, keys):
        if keys.get('menu_up'):
            self.selected = (self.selected - 1) % len(self.options)
            return 'move'
        if keys.get('menu_down'):
            self.selected = (self.selected + 1) % len(self.options)
            return 'move'
        if keys.get('menu_select') or (keys.get('pause') and self.selected == 0):
            self.result = ['resume', 'restart', 'quit'][self.selected]
            return 'select'
        if keys.get('menu_back') or keys.get('pause'):
            self.result = 'resume'
            return 'select'
        return None

    def draw(self, surface):
        # Darken background
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Center box
        bw, bh = 170, 110
        bx = (INTERNAL_WIDTH - bw) // 2
        by = (INTERNAL_HEIGHT - bh) // 2
        _draw_box(surface, bx, by, bw, bh, fill=UI_BG, border=UI_BORDER)

        # Title
        _font_md.draw(surface, "PAUSED", INTERNAL_WIDTH // 2, by + 14,
                      UI_TITLE, center=True)

        # Divider inside box
        pygame.draw.line(surface, UI_BORDER,
                         (bx + 10, by + 30), (bx + bw - 10, by + 30))

        # Options
        for i, opt in enumerate(self.options):
            y = by + 42 + i * 20
            is_sel = (i == self.selected)
            color = UI_SELECTED if is_sel else UI_TEXT
            prefix = "> " if is_sel else "  "
            _font_sm.draw(surface, prefix + opt.upper(), INTERNAL_WIDTH // 2, y,
                          color, center=True)


# ─── Level Complete Screen ────────────────────────────────
class LevelCompleteScreen:
    """Shown after completing a level."""

    def __init__(self, level_index, time_seconds, coins, mode='story'):
        self.level_index = level_index
        self.time = time_seconds
        self.coins = coins
        self.mode = mode
        self.rank = None
        self.is_best = False

        if mode == 'arcade':
            self.rank, self.is_best = leaderboard.add_time(level_index, time_seconds)

        self.options = []
        if mode == 'story' and level_index < len(LEVEL_NAMES) - 1:
            self.options.append("Next Level")
        self.options.append("Replay")
        self.options.append("Level Select")

        self.selected = 0
        self.result = None
        self._timer = 0

    def handle_input(self, keys):
        if self._timer < 30:
            return None
        if keys.get('menu_up'):
            self.selected = (self.selected - 1) % len(self.options)
            return 'move'
        if keys.get('menu_down'):
            self.selected = (self.selected + 1) % len(self.options)
            return 'move'
        if keys.get('menu_select'):
            choice = self.options[self.selected].lower().replace(' ', '_')
            self.result = choice
            return 'select'
        return None

    def update(self):
        self._timer += 1

    def draw(self, surface):
        # Darken background
        overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        cy = INTERNAL_HEIGHT // 2

        # Box
        bw, bh = 220, 180
        bx = (INTERNAL_WIDTH - bw) // 2
        by = cy - bh // 2
        _draw_box(surface, bx, by, bw, bh, fill=(18, 18, 22), border=UI_BORDER)

        # Title
        _font_md.draw(surface, "LEVEL COMPLETE!", INTERNAL_WIDTH // 2, by + 16,
                      UI_TITLE, center=True)

        # Level name
        _font_sm.draw(surface, LEVEL_NAMES[self.level_index].upper(),
                      INTERNAL_WIDTH // 2, by + 36, UI_TEXT_DIM, center=True)

        # Divider
        pygame.draw.line(surface, UI_BORDER,
                         (bx + 10, by + 48), (bx + bw - 10, by + 48))

        # Stats
        stats_y = by + 58
        time_str = leaderboard.format_time(self.time)
        _font_sm.draw(surface, "TIME: " + time_str, bx + 20, stats_y, UI_TEXT)

        # Par comparison
        par = LEVEL_PAR_TIMES[self.level_index]
        if self.time <= par:
            _font_sm.draw(surface, "UNDER PAR!", bx + bw - 20, stats_y,
                          (120, 170, 110), right=True)

        _font_sm.draw(surface, "COINS: " + str(self.coins), bx + 20, stats_y + 14, UI_TEXT)

        # Arcade rank
        if self.mode == 'arcade' and self.rank:
            rank_y = stats_y + 30
            rank_text = "RANK #" + str(self.rank)
            if self.is_best:
                rank_text += "  NEW BEST!"
            _font_sm.draw(surface, rank_text, INTERNAL_WIDTH // 2, rank_y,
                          UI_HIGHLIGHT if self.is_best else UI_TEXT, center=True)

            # Leaderboard preview
            times = leaderboard.get_times(self.level_index)[:5]
            if times:
                lb_y = rank_y + 14
                _font_sm.draw(surface, "TOP TIMES", INTERNAL_WIDTH // 2, lb_y,
                              UI_TEXT_DIM, center=True)
                for j, t in enumerate(times):
                    _font_sm.draw(surface, str(j + 1) + ". " + leaderboard.format_time(t),
                                  INTERNAL_WIDTH // 2, lb_y + 12 + j * 10,
                                  UI_TEXT, center=True)

        # Options
        opt_start = by + bh - 10 - len(self.options) * 18
        if self._timer >= 30:
            for i, opt in enumerate(self.options):
                y = opt_start + i * 18
                is_sel = (i == self.selected)
                color = UI_SELECTED if is_sel else UI_TEXT
                prefix = "> " if is_sel else "  "
                _font_sm.draw(surface, prefix + opt.upper(), INTERNAL_WIDTH // 2,
                              y, color, center=True)


# ─── Settings Menu ────────────────────────────────────────
class SettingsMenu:
    """Settings with volume bars and toggles."""

    def __init__(self, settings):
        self.settings = settings
        self.options = ["Music Volume", "SFX Volume", "Fullscreen", "Back"]
        self.selected = 0
        self.result = None

    def handle_input(self, keys):
        if keys.get('menu_up'):
            self.selected = (self.selected - 1) % len(self.options)
            return 'move'
        if keys.get('menu_down'):
            self.selected = (self.selected + 1) % len(self.options)
            return 'move'
        if keys.get('menu_back'):
            self.result = 'back'
            return 'select'

        opt = self.options[self.selected]
        if opt == "Music Volume":
            if keys.get('menu_left'):
                self.settings['music_vol'] = max(0, round(self.settings['music_vol'] - 0.1, 1))
                return 'move'
            if keys.get('menu_right'):
                self.settings['music_vol'] = min(1, round(self.settings['music_vol'] + 0.1, 1))
                return 'move'
        elif opt == "SFX Volume":
            if keys.get('menu_left'):
                self.settings['sfx_vol'] = max(0, round(self.settings['sfx_vol'] - 0.1, 1))
                return 'move'
            if keys.get('menu_right'):
                self.settings['sfx_vol'] = min(1, round(self.settings['sfx_vol'] + 0.1, 1))
                return 'move'
        elif opt == "Fullscreen":
            if keys.get('menu_select') or keys.get('menu_left') or keys.get('menu_right'):
                self.settings['fullscreen'] = not self.settings['fullscreen']
                self.result = 'toggle_fullscreen'
                return 'select'
        elif opt == "Back":
            if keys.get('menu_select'):
                self.result = 'back'
                return 'select'
        return None

    def draw(self, surface):
        surface.fill(UI_BG)

        # Title
        _font_md.draw(surface, "SETTINGS", INTERNAL_WIDTH // 2, 22, UI_TITLE, center=True)
        _hline(surface, 40)

        # Options
        for i, opt in enumerate(self.options):
            y = 58 + i * 34
            is_sel = (i == self.selected)
            color = UI_SELECTED if is_sel else UI_TEXT
            prefix = "> " if is_sel else "  "

            if opt == "Music Volume":
                _font_sm.draw(surface, prefix + "MUSIC VOLUME", 40, y, color)
                _draw_volume_bar(surface, INTERNAL_WIDTH - 130, y + 1,
                                 self.settings['music_vol'], is_sel)
                pct = str(int(self.settings['music_vol'] * 100)) + "%"
                _font_sm.draw(surface, pct, INTERNAL_WIDTH - 40, y, UI_TEXT_DIM)
            elif opt == "SFX Volume":
                _font_sm.draw(surface, prefix + "SFX VOLUME", 40, y, color)
                _draw_volume_bar(surface, INTERNAL_WIDTH - 130, y + 1,
                                 self.settings['sfx_vol'], is_sel)
                pct = str(int(self.settings['sfx_vol'] * 100)) + "%"
                _font_sm.draw(surface, pct, INTERNAL_WIDTH - 40, y, UI_TEXT_DIM)
            elif opt == "Fullscreen":
                state = "ON" if self.settings['fullscreen'] else "OFF"
                _font_sm.draw(surface, prefix + "FULLSCREEN: " + state, 40, y, color)
            else:
                _font_sm.draw(surface, prefix + opt.upper(), 40, y, color)

        # Footer
        _hline(surface, INTERNAL_HEIGHT - 26)
        _font_sm.draw(surface, "LEFT/RIGHT: ADJUST   ESC: BACK",
                      INTERNAL_WIDTH // 2, INTERNAL_HEIGHT - 14,
                      UI_TEXT_DIM, center=True)


# ─── HUD ──────────────────────────────────────────────────
class HUD:
    """In-game heads-up display with 8-bit font."""

    def draw(self, surface, level_name, time_seconds, coins, mode='story'):
        # Level name (top-left)
        _font_sm.draw(surface, level_name.upper(), 6, 4, UI_TEXT)

        # Timer (top-center)
        time_str = leaderboard.format_time(time_seconds)
        _font_md.draw(surface, time_str, INTERNAL_WIDTH // 2, 4, UI_TITLE, center=True)

        # Mode indicator
        if mode == 'arcade':
            _font_sm.draw(surface, "ARCADE", INTERNAL_WIDTH // 2, 20,
                          (170, 130, 90), center=True)

        # Coin icon (small pixel circle)
        cx_coin = INTERNAL_WIDTH - 40
        cy_coin = 8
        pygame.draw.circle(surface, (185, 165, 85), (cx_coin, cy_coin), 4)
        pygame.draw.circle(surface, (220, 205, 130), (cx_coin, cy_coin), 2)

        # Coin count
        _font_sm.draw(surface, "x" + str(coins), cx_coin + 8, 3, UI_TEXT)


# ─── Helper: Volume bar ──────────────────────────────────
def _draw_volume_bar(surface, x, y, vol, active=False):
    """Draw a segmented volume bar."""
    segments = 10
    seg_w = 6
    seg_h = 6
    gap = 2
    filled = int(vol * segments)

    for s in range(segments):
        sx = x + s * (seg_w + gap)
        if s < filled:
            color = UI_HIGHLIGHT if active else UI_TEXT
        else:
            color = (40, 40, 45)
        pygame.draw.rect(surface, color, (sx, y, seg_w, seg_h))
