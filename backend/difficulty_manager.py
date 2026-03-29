"""
difficulty_manager.py
Dynamic difficulty adjustment and procedural level generation.
"""

import random
import copy
from typing import List, Dict, Optional
from game_engine import GRADIENT_COLORS, Tube


# ---------------------------------------------------------------------------
# Pre-designed levels 1–10
# ---------------------------------------------------------------------------

def _tube(capacity: int, layers: list) -> dict:
    return {"capacity": capacity, "layers": layers}


PREDEFINED_LEVELS = {
    1: {
        "level": 1, "name": "Warm Up",
        "number_of_tubes": 4, "tube_capacity": 4,
        "number_of_colors": 2,
        "tubes": [
            _tube(4, ["red", "blue", "red", "blue"]),
            _tube(4, ["blue", "red", "blue", "red"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    2: {
        "level": 2, "name": "Getting Started",
        "number_of_tubes": 5, "tube_capacity": 4,
        "number_of_colors": 3,
        "tubes": [
            _tube(4, ["red", "blue", "green", "red"]),
            _tube(4, ["green", "red", "blue", "green"]),
            _tube(4, ["blue", "green", "red", "blue"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    3: {
        "level": 3, "name": "Three Colors",
        "number_of_tubes": 5, "tube_capacity": 4,
        "number_of_colors": 3,
        "tubes": [
            _tube(4, ["yellow", "red", "blue", "yellow"]),
            _tube(4, ["blue", "yellow", "red", "blue"]),
            _tube(4, ["red", "blue", "yellow", "red"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    4: {
        "level": 4, "name": "Four Colors",
        "number_of_tubes": 6, "tube_capacity": 4,
        "number_of_colors": 4,
        "tubes": [
            _tube(4, ["red", "green", "blue", "purple"]),
            _tube(4, ["blue", "purple", "red", "green"]),
            _tube(4, ["green", "red", "purple", "blue"]),
            _tube(4, ["purple", "blue", "green", "red"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    5: {
        "level": 5, "name": "Rising Challenge",
        "number_of_tubes": 7, "tube_capacity": 4,
        "number_of_colors": 5,
        "tubes": [
            _tube(4, ["orange", "red", "blue", "green"]),
            _tube(4, ["green", "orange", "purple", "red"]),
            _tube(4, ["blue", "purple", "orange", "green"]),
            _tube(4, ["purple", "green", "red", "orange"]),
            _tube(4, ["red", "blue", "green", "purple"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    6: {
        "level": 6, "name": "Complex Mix",
        "number_of_tubes": 8, "tube_capacity": 4,
        "number_of_colors": 6,
        "tubes": [
            _tube(4, ["teal", "red", "blue", "orange"]),
            _tube(4, ["orange", "teal", "purple", "red"]),
            _tube(4, ["blue", "orange", "teal", "green"]),
            _tube(4, ["purple", "green", "red", "teal"]),
            _tube(4, ["red", "blue", "green", "purple"]),
            _tube(4, ["green", "purple", "orange", "blue"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    7: {
        "level": 7, "name": "Seven Colors",
        "number_of_tubes": 9, "tube_capacity": 4,
        "number_of_colors": 7,
        "tubes": [
            _tube(4, ["pink", "teal", "red", "blue"]),
            _tube(4, ["orange", "pink", "purple", "red"]),
            _tube(4, ["blue", "orange", "teal", "green"]),
            _tube(4, ["purple", "green", "red", "teal"]),
            _tube(4, ["red", "blue", "green", "purple"]),
            _tube(4, ["green", "purple", "orange", "pink"]),
            _tube(4, ["teal", "red", "pink", "orange"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    8: {
        "level": 8, "name": "Expert",
        "number_of_tubes": 10, "tube_capacity": 4,
        "number_of_colors": 8,
        "tubes": [
            _tube(4, ["lime", "pink", "teal", "red"]),
            _tube(4, ["orange", "lime", "purple", "red"]),
            _tube(4, ["blue", "orange", "teal", "green"]),
            _tube(4, ["purple", "green", "red", "teal"]),
            _tube(4, ["red", "blue", "green", "purple"]),
            _tube(4, ["green", "purple", "orange", "lime"]),
            _tube(4, ["teal", "red", "pink", "orange"]),
            _tube(4, ["pink", "lime", "blue", "teal"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    9: {
        "level": 9, "name": "Master",
        "number_of_tubes": 11, "tube_capacity": 4,
        "number_of_colors": 9,
        "tubes": [
            _tube(4, ["navy", "lime", "pink", "teal"]),
            _tube(4, ["orange", "navy", "purple", "red"]),
            _tube(4, ["blue", "orange", "teal", "green"]),
            _tube(4, ["purple", "green", "red", "teal"]),
            _tube(4, ["red", "blue", "green", "purple"]),
            _tube(4, ["green", "purple", "orange", "lime"]),
            _tube(4, ["teal", "red", "pink", "orange"]),
            _tube(4, ["pink", "lime", "blue", "navy"]),
            _tube(4, ["lime", "navy", "orange", "pink"]),
            _tube(4, []), _tube(4, []),
        ],
    },
    10: {
        "level": 10, "name": "Grand Master",
        "number_of_tubes": 12, "tube_capacity": 4,
        "number_of_colors": 10,
        "tubes": [
            _tube(4, ["navy", "lime", "pink", "teal"]),
            _tube(4, ["orange", "navy", "purple", "red"]),
            _tube(4, ["blue", "orange", "teal", "green"]),
            _tube(4, ["purple", "green", "red", "teal"]),
            _tube(4, ["red", "blue", "green", "purple"]),
            _tube(4, ["green", "purple", "orange", "lime"]),
            _tube(4, ["teal", "red", "pink", "orange"]),
            _tube(4, ["pink", "lime", "blue", "navy"]),
            _tube(4, ["lime", "navy", "orange", "pink"]),
            _tube(4, ["yellow", "pink", "navy", "lime"]),
            _tube(4, []), _tube(4, []),
        ],
    },
}


class DifficultyManager:
    """
    Adjusts difficulty dynamically based on player performance.
    Also generates procedural levels beyond level 10.
    """

    # Scoring bands (seconds)
    EXPECTED_TIMES = {1: 30, 2: 45, 3: 60, 4: 90, 5: 120,
                      6: 150, 7: 180, 8: 240, 9: 300, 10: 360}

    def __init__(self):
        self.difficulty_score: float = 0.5   # 0.0 easy → 1.0 hard
        self.current_level: int = 1

    def adjust(self, level: int, time_taken: float, expected_time: Optional[float] = None):
        """
        Update internal difficulty score after a level is completed.
        """
        expected = expected_time or self.EXPECTED_TIMES.get(level, 120)
        ratio = time_taken / max(expected, 1)

        if ratio < 0.5:         # Very fast → increase difficulty
            delta = +0.15
        elif ratio < 0.8:
            delta = +0.07
        elif ratio < 1.2:
            delta = 0.0         # On par → no change
        elif ratio < 1.8:
            delta = -0.07
        else:                   # Very slow → ease off
            delta = -0.15

        self.difficulty_score = max(0.0, min(1.0, self.difficulty_score + delta))
        return self.difficulty_score

    def get_level_config(self, level: int) -> dict:
        """Return level config, either predefined or procedurally generated."""
        if level in PREDEFINED_LEVELS:
            return copy.deepcopy(PREDEFINED_LEVELS[level])
        # Generate procedural level for levels > 10
        return self._generate_procedural(level)

    def _generate_procedural(self, level: int) -> dict:
        """Generate a guaranteed-solvable level procedurally."""
        # Scale complexity with level + difficulty score
        base_colors = min(10, 4 + (level - 10) // 2 + int(self.difficulty_score * 3))
        n_colors = min(10, base_colors)
        tube_capacity = 4
        n_empty = max(2, int(2 + (1 - self.difficulty_score) * 2))
        n_tubes = n_colors + n_empty

        color_ids = [c["id"] for c in GRADIENT_COLORS[:n_colors]]

        # Build solved state: each color fills one tube
        tubes_solved = [[c] * tube_capacity for c in color_ids]
        # Add empty tubes
        for _ in range(n_empty):
            tubes_solved.append([])

        # Shuffle to create puzzle state (reverse-solvable)
        tubes = [list(t) for t in tubes_solved]
        for _ in range(level * 20 + 50):
            # Random valid pour to scramble
            non_empty = [i for i, t in enumerate(tubes) if t]
            non_full = [i for i, t in enumerate(tubes) if len(t) < tube_capacity]
            if not non_empty or not non_full:
                break
            src = random.choice(non_empty)
            dst = random.choice([i for i in non_full if i != src] or non_full)
            if src == dst:
                continue
            color = tubes[src][-1]
            if tubes[dst] and tubes[dst][-1] != color:
                continue
            space = tube_capacity - len(tubes[dst])
            top_c = sum(1 for l in reversed(tubes[src]) if l == color)
            move_n = min(top_c, space)
            for _ in range(move_n):
                tubes[src].pop()
                tubes[dst].append(color)

        tube_dicts = [_tube(tube_capacity, t) for t in tubes]

        return {
            "level": level,
            "name": f"Level {level}",
            "number_of_tubes": n_tubes,
            "tube_capacity": tube_capacity,
            "number_of_colors": n_colors,
            "tubes": tube_dicts,
        }