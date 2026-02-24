"""
GRIT - A Retro Platformer
Keep Moving. Keep Climbing. Stay Gritty.

Created by Noah Crandall in cooperation with Anthropic Claude
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Windows AppUserModelID BEFORE pygame loads, so taskbar uses our icon
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('noahcrandall.grit.game.1')
except Exception:
    pass

from src.engine import Engine


def main():
    engine = Engine()
    engine.run()


if __name__ == '__main__':
    main()
