"""
GRIT - Game Engine
Main game loop, state machine, input handling, and rendering pipeline.
"""

import os
import sys
import ctypes
import ctypes.wintypes
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, INTERNAL_WIDTH, INTERNAL_HEIGHT,
    DISPLAY_SCALE, FPS, GAME_TITLE, TILE,
    JOY_JUMP, JOY_DASH, JOY_PAUSE, JOY_BACK, JOY_DEADZONE,
    LEVEL_NAMES, get_base_dir,
)
from src.sprites import CharacterSprites, TileSprites
from src.audio import AudioManager
from src.particles import ParticleManager
from src.player import Player
from src.level import Level, Camera
from src.menu import (
    SplashScreen, MainMenu, LevelSelect, PauseMenu,
    LevelCompleteScreen, SettingsMenu, HUD,
)
from src import leaderboard


# ─── Game States ──────────────────────────────────────────
class State:
    SPLASH = 'splash'
    MENU = 'menu'
    LEVEL_SELECT = 'level_select'
    PLAYING = 'playing'
    PAUSED = 'paused'
    LEVEL_COMPLETE = 'level_complete'
    SETTINGS = 'settings'


class Engine:
    """Core game engine managing all state and rendering."""

    def __init__(self):
        pygame.init()

        # Set icon BEFORE set_mode so Windows picks it up for the taskbar
        pygame.display.set_icon(self._make_icon())

        # Display
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(GAME_TITLE)

        # Also force the icon via Win32 API for the taskbar
        self._set_windows_icon()

        # Internal render surface (pixel-art resolution)
        self.internal = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)

        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False

        # ── Systems ──
        self.audio = AudioManager()
        self.char_sprites = CharacterSprites(scale=2)
        self.tile_sprites = TileSprites()
        self.particles = ParticleManager()
        self.camera = Camera()
        self.hud = HUD()

        # ── State ──
        self.state = State.SPLASH
        self.splash = SplashScreen()
        self.main_menu = MainMenu()
        self.level_select = None
        self.pause_menu = None
        self.complete_screen = None
        self.settings_menu = None

        # ── Game state ──
        self.current_level = None
        self.player = None
        self.game_mode = 'story'  # 'story' or 'arcade'
        self.level_timer = 0.0
        self.unlocked_levels = leaderboard.load_progress()
        self.tick = 0

        # ── Controller ──
        self.joysticks = []
        self._init_joysticks()

        # ── Input state (for edge detection) ──
        self._prev_keys = {}
        self._prev_hat = (0, 0)
        self._settings = {
            'music_vol': 0.4,
            'sfx_vol': 0.6,
            'fullscreen': False,
        }

    def _init_joysticks(self):
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)
            print(f"[Controller] Found: {joy.get_name()}")

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.tick += 1

            # ── Events ──
            keys = self._process_events()

            # ── Update ──
            self._update(keys, dt)

            # ── Draw ──
            self._draw()

            # ── Present ──
            scaled = pygame.transform.scale(self.internal, self.screen.get_size())
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _process_events(self):
        """Process pygame events and return input dict."""
        keys = {
            'left': False, 'right': False,
            'jump': False, 'jump_pressed': False,
            'dash_pressed': False,
            'pause': False,
            'menu_up': False, 'menu_down': False,
            'menu_left': False, 'menu_right': False,
            'menu_select': False, 'menu_back': False,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return keys

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()

                if event.key in (pygame.K_UP, pygame.K_w):
                    keys['menu_up'] = True
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    keys['menu_down'] = True
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    keys['menu_left'] = True
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    keys['menu_right'] = True
                if event.key == pygame.K_RETURN:
                    keys['menu_select'] = True
                if event.key == pygame.K_ESCAPE:
                    keys['menu_back'] = True
                    keys['pause'] = True

                if event.key in (pygame.K_UP, pygame.K_w):
                    keys['jump_pressed'] = True
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    keys['dash_pressed'] = True

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == JOY_JUMP:
                    keys['jump_pressed'] = True
                    keys['menu_select'] = True
                if event.button == JOY_DASH:
                    keys['dash_pressed'] = True
                if event.button == JOY_PAUSE:
                    keys['pause'] = True
                if event.button == JOY_BACK:
                    keys['menu_back'] = True

            # Re-init joysticks if one is added/removed
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self._init_joysticks()

            # Mouse click — check for secret cheat on main menu
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == State.MENU:
                    # Convert screen coords to internal coords
                    sw, sh = self.screen.get_size()
                    ix = int(event.pos[0] * INTERNAL_WIDTH / sw)
                    iy = int(event.pos[1] * INTERNAL_HEIGHT / sh)
                    if self.main_menu.handle_mouse_click(ix, iy):
                        self.unlocked_levels = len(LEVEL_NAMES)
                        self.audio.play_sfx('complete')

        # Held keys
        pressed = pygame.key.get_pressed()
        keys['left'] = pressed[pygame.K_LEFT] or pressed[pygame.K_a]
        keys['right'] = pressed[pygame.K_RIGHT] or pressed[pygame.K_d]
        keys['jump'] = pressed[pygame.K_UP] or pressed[pygame.K_w]

        # Controller held state
        cur_hat = (0, 0)
        for joy in self.joysticks:
            try:
                # D-pad (edge-detected for menus, held for movement)
                if joy.get_numhats() > 0:
                    hat = joy.get_hat(0)
                    cur_hat = hat
                    if hat[0] < 0:
                        keys['left'] = True
                    if hat[0] > 0:
                        keys['right'] = True
                    # Edge detection: only trigger on new press
                    if hat[1] > 0 and self._prev_hat[1] <= 0:
                        keys['menu_up'] = True
                    if hat[1] < 0 and self._prev_hat[1] >= 0:
                        keys['menu_down'] = True
                    if hat[0] < 0 and self._prev_hat[0] >= 0:
                        keys['menu_left'] = True
                    if hat[0] > 0 and self._prev_hat[0] <= 0:
                        keys['menu_right'] = True

                # Left stick
                if joy.get_numaxes() >= 2:
                    axis_x = joy.get_axis(0)
                    axis_y = joy.get_axis(1)
                    if axis_x < -JOY_DEADZONE:
                        keys['left'] = True
                    if axis_x > JOY_DEADZONE:
                        keys['right'] = True

                # Jump held
                if joy.get_numbuttons() > JOY_JUMP:
                    keys['jump'] = keys['jump'] or joy.get_button(JOY_JUMP)
            except Exception:
                pass

        self._prev_hat = cur_hat
        self._prev_keys = keys.copy()
        return keys

    def _update(self, keys, dt):
        """Update current state."""
        if self.state == State.SPLASH:
            self.splash.update()
            if self.splash.done:
                self.state = State.MENU
                self.audio.play_menu_music()

        elif self.state == State.MENU:
            self.main_menu.update()
            action = self.main_menu.handle_input(keys)
            if action == 'move':
                self.audio.play_sfx('menu_move')
            elif action == 'select':
                self.audio.play_sfx('menu_select')
                result = self.main_menu.result
                self.main_menu.result = None
                if result == 'story_mode':
                    self.game_mode = 'story'
                    self.level_select = LevelSelect('story', self.unlocked_levels)
                    self.state = State.LEVEL_SELECT
                elif result == 'arcade_mode':
                    self.game_mode = 'arcade'
                    self.level_select = LevelSelect('arcade', self.unlocked_levels)
                    self.state = State.LEVEL_SELECT
                elif result == 'settings':
                    self.settings_menu = SettingsMenu(self._settings)
                    self.state = State.SETTINGS
                elif result == 'quit':
                    self.running = False

        elif self.state == State.LEVEL_SELECT:
            action = self.level_select.handle_input(keys)
            if action == 'move':
                self.audio.play_sfx('menu_move')
            elif action == 'select':
                self.audio.play_sfx('menu_select')
                result = self.level_select.result
                self.level_select.result = None
                if result == 'back':
                    self.state = State.MENU
                elif isinstance(result, int):
                    self._start_level(result)

        elif self.state == State.SETTINGS:
            action = self.settings_menu.handle_input(keys)
            if action == 'move':
                self.audio.play_sfx('menu_move')
            elif action == 'select':
                self.audio.play_sfx('menu_select')
                result = self.settings_menu.result
                self.settings_menu.result = None
                if result == 'back':
                    self.state = State.MENU
                elif result == 'toggle_fullscreen':
                    self._toggle_fullscreen()
            # Apply volume changes
            self.audio.set_music_volume(self._settings['music_vol'])

        elif self.state == State.PLAYING:
            self._update_gameplay(keys, dt)

        elif self.state == State.PAUSED:
            action = self.pause_menu.handle_input(keys)
            if action == 'move':
                self.audio.play_sfx('menu_move')
            elif action == 'select':
                self.audio.play_sfx('menu_select')
                result = self.pause_menu.result
                self.pause_menu.result = None
                if result == 'resume':
                    self.state = State.PLAYING
                elif result == 'restart':
                    self._start_level(self.current_level.index)
                elif result == 'quit':
                    self.state = State.MENU
                    self.audio.play_menu_music()

        elif self.state == State.LEVEL_COMPLETE:
            self.complete_screen.update()
            action = self.complete_screen.handle_input(keys)
            if action == 'move':
                self.audio.play_sfx('menu_move')
            elif action == 'select':
                self.audio.play_sfx('menu_select')
                result = self.complete_screen.result
                self.complete_screen.result = None
                if result == 'next_level':
                    next_idx = self.current_level.index + 1
                    if next_idx < len(LEVEL_NAMES):
                        self._start_level(next_idx)
                    else:
                        self.state = State.MENU
                        self.audio.play_menu_music()
                elif result == 'replay':
                    self._start_level(self.current_level.index)
                elif result == 'level_select':
                    self.level_select = LevelSelect(self.game_mode, self.unlocked_levels)
                    self.state = State.LEVEL_SELECT
                    self.audio.play_menu_music()

    def _start_level(self, level_index):
        """Initialize and start a level."""
        self.current_level = Level(level_index, self.tile_sprites)
        sx, sy = self.current_level.start_pos
        self.player = Player(sx, sy, self.char_sprites, self.particles, self.audio)
        self.particles.clear()
        self.camera.snap(self.player.center_x, self.player.center_y, self.current_level)
        self.level_timer = 0.0
        self.state = State.PLAYING
        self.audio.play_gameplay_music()

    def _update_gameplay(self, keys, dt):
        """Update active gameplay."""
        # Pause
        if keys.get('pause'):
            self.pause_menu = PauseMenu()
            self.state = State.PAUSED
            return

        # Player input
        self.player.handle_input(keys)

        # Update level (moving platforms)
        self.current_level.update()

        # Update player
        result = self.player.update(self.current_level)

        if result == 'complete':
            # Level complete!
            self.audio.play_sfx('complete')
            self.audio.stop_music()
            # Unlock next level
            if self.game_mode == 'story':
                new_unlocked = max(self.unlocked_levels, self.current_level.index + 2)
                new_unlocked = min(new_unlocked, len(LEVEL_NAMES))
                if new_unlocked > self.unlocked_levels:
                    self.unlocked_levels = new_unlocked
                    leaderboard.save_progress(self.unlocked_levels)

            self.complete_screen = LevelCompleteScreen(
                self.current_level.index, self.level_timer,
                self.player.coins, self.game_mode
            )
            self.state = State.LEVEL_COMPLETE
            return

        if result is True:
            # Player death animation done, respawn
            self.player.respawn()
            self.camera.snap(self.player.center_x, self.player.center_y, self.current_level)
            # Reset timer in arcade mode on death
            if self.game_mode == 'arcade':
                self.level_timer = 0.0
                # Reload level coins
                self.current_level = Level(self.current_level.index, self.tile_sprites)
                sx, sy = self.current_level.start_pos
                self.player.spawn_x = sx
                self.player.spawn_y = sy
                self.player.respawn()
                self.player.coins = 0

        # Timer
        if self.player.alive:
            self.level_timer += dt

        # Camera
        if self.player.alive:
            self.camera.update(self.player.center_x, self.player.center_y, self.current_level)

        # Particles
        self.particles.update()

        # Exit sparkle
        if self.current_level.exit_pos:
            ex, ey = self.current_level.exit_pos
            self.particles.emit_exit_sparkle(
                ex * TILE, (ey - 1) * TILE, TILE * 2
            )

    def _draw(self):
        """Draw current state to internal surface."""
        if self.state == State.SPLASH:
            self.splash.draw(self.internal)

        elif self.state == State.MENU:
            self.main_menu.draw(self.internal)

        elif self.state == State.LEVEL_SELECT:
            self.level_select.draw(self.internal)

        elif self.state == State.SETTINGS:
            self.settings_menu.draw(self.internal)

        elif self.state in (State.PLAYING, State.PAUSED, State.LEVEL_COMPLETE):
            self._draw_gameplay()
            if self.state == State.PAUSED:
                self.pause_menu.draw(self.internal)
            elif self.state == State.LEVEL_COMPLETE:
                self.complete_screen.draw(self.internal)

    def _draw_gameplay(self):
        """Render the active gameplay scene."""
        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)

        # Background
        self.current_level.draw_background(self.internal, cam_x, cam_y)

        # Level tiles
        self.current_level.draw(self.internal, cam_x, cam_y, self.tick)

        # Particles (behind player)
        self.particles.draw(self.internal, cam_x, cam_y)

        # Player
        self.player.draw(self.internal, cam_x, cam_y)

        # HUD
        self.hud.draw(
            self.internal,
            self.current_level.name,
            self.level_timer,
            self.player.coins,
            self.game_mode
        )

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._settings['fullscreen'] = self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
            )

    @staticmethod
    def _make_icon():
        """Generate a 64×64 pixel icon with a chunky 'G' for the taskbar/title bar."""
        size = 64
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        # Dark background with subtle border
        pygame.draw.rect(icon, (22, 22, 24), (0, 0, size, size))
        pygame.draw.rect(icon, (80, 80, 85), (0, 0, size, size), 1)
        # 'G' glyph on a 7×9 grid
        g = [
            " ##### ",
            "##   ##",
            "##     ",
            "##     ",
            "## ####",
            "##   ##",
            "##   ##",
            "##   ##",
            " ##### ",
        ]
        px = 6
        ox = (size - 7 * px) // 2
        oy = (size - 9 * px) // 2
        color = (210, 210, 215)
        for r, row in enumerate(g):
            for c, ch in enumerate(row):
                if ch == '#':
                    pygame.draw.rect(icon, color, (ox + c * px, oy + r * px, px, px))
        return icon

    @staticmethod
    def _set_windows_icon():
        """Set the taskbar icon via Win32 API using the .ico file."""
        try:
            ico_path = os.path.join(get_base_dir(), 'grit.ico')
            if not os.path.exists(ico_path):
                return

            user32 = ctypes.windll.user32

            # Set up proper arg/return types for LoadImageW
            user32.LoadImageW.restype = ctypes.wintypes.HANDLE
            user32.LoadImageW.argtypes = [
                ctypes.wintypes.HINSTANCE, ctypes.wintypes.LPCWSTR,
                ctypes.wintypes.UINT, ctypes.c_int, ctypes.c_int,
                ctypes.wintypes.UINT,
            ]

            # Set up proper arg/return types for SendMessageW
            user32.SendMessageW.restype = ctypes.c_long
            user32.SendMessageW.argtypes = [
                ctypes.wintypes.HWND, ctypes.wintypes.UINT,
                ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM,
            ]

            IMAGE_ICON = 1
            LR_LOADFROMFILE = 0x0010
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1

            # Load both sizes from .ico
            hicon_big = user32.LoadImageW(None, ico_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
            hicon_small = user32.LoadImageW(None, ico_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

            # Get pygame's window handle
            hwnd = pygame.display.get_wm_info()['window']

            if hicon_big:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
            if hicon_small:
                user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        except Exception:
            pass
