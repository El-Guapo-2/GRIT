"""
GRIT - Leaderboard System
Saves and loads best times per level for Arcade Mode.
"""

import json
import os
from config import get_data_dir, LEVEL_NAMES

LEADERBOARD_FILE = "leaderboard.json"
MAX_ENTRIES = 10


def _path():
    return os.path.join(get_data_dir(), LEADERBOARD_FILE)


def load():
    """Load leaderboard data. Returns dict mapping level_index → list of times."""
    try:
        with open(_path(), 'r') as f:
            data = json.load(f)
        # Ensure all levels exist
        result = {}
        for i in range(len(LEVEL_NAMES)):
            key = str(i)
            result[key] = sorted(data.get(key, []))[:MAX_ENTRIES]
        return result
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {str(i): [] for i in range(len(LEVEL_NAMES))}


def save(data):
    """Save leaderboard data to disk."""
    try:
        with open(_path(), 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Leaderboard] Could not save: {e}")


def add_time(level_index, time_seconds):
    """Add a new time entry for a level. Returns (rank, is_new_best)."""
    data = load()
    key = str(level_index)
    times = data.get(key, [])
    is_new_best = len(times) == 0 or time_seconds < min(times)
    times.append(round(time_seconds, 3))
    times.sort()
    data[key] = times[:MAX_ENTRIES]
    save(data)
    rank = data[key].index(round(time_seconds, 3)) + 1
    return rank, is_new_best


def get_times(level_index):
    """Get sorted times for a level."""
    data = load()
    return data.get(str(level_index), [])


def get_best_time(level_index):
    """Get the best time for a level, or None."""
    times = get_times(level_index)
    return times[0] if times else None


def format_time(seconds):
    """Format seconds into M:SS.mmm display string."""
    if seconds is None:
        return "--:--.---"
    m = int(seconds) // 60
    s = seconds - m * 60
    return f"{m}:{s:06.3f}"


def load_progress():
    """Load game progress (unlocked levels)."""
    path = os.path.join(get_data_dir(), "progress.json")
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return data.get("unlocked", 1)
    except (FileNotFoundError, json.JSONDecodeError):
        return 1


def save_progress(unlocked):
    """Save game progress."""
    path = os.path.join(get_data_dir(), "progress.json")
    try:
        with open(path, 'w') as f:
            json.dump({"unlocked": unlocked}, f)
    except Exception:
        pass
