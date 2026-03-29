"""
game_engine.py
Core Water Sort Puzzle game logic — fully separated from API layer.
Handles tube state, move validation, win detection, undo/redo stack.
"""

import copy
import random
from typing import List, Optional, Tuple, Dict


# ---------------------------------------------------------------------------
# Color / Layer definitions
# ---------------------------------------------------------------------------

GRADIENT_COLORS = [
    {"id": "red",    "css": "linear-gradient(180deg,#ff4e50,#fc466b)",  "name": "Red"},
    {"id": "blue",   "css": "linear-gradient(180deg,#2980b9,#6dd5fa)",  "name": "Blue"},
    {"id": "green",  "css": "linear-gradient(180deg,#11998e,#38ef7d)",  "name": "Green"},
    {"id": "yellow", "css": "linear-gradient(180deg,#f7971e,#ffd200)",  "name": "Yellow"},
    {"id": "purple", "css": "linear-gradient(180deg,#834d9b,#d04ed6)",  "name": "Purple"},
    {"id": "orange", "css": "linear-gradient(180deg,#f46b45,#eea849)",  "name": "Orange"},
    {"id": "teal",   "css": "linear-gradient(180deg,#009fff,#ec2f4b)",  "name": "Teal"},
    {"id": "pink",   "css": "linear-gradient(180deg,#ee0979,#ff6a00)",  "name": "Pink"},
    {"id": "lime",   "css": "linear-gradient(180deg,#96e6a1,#d4fc79)",  "name": "Lime"},
    {"id": "navy",   "css": "linear-gradient(180deg,#0f0c29,#302b63)",  "name": "Navy"},
]


class Tube:
    """Represents a single tube containing liquid layers (bottom → top)."""

    def __init__(self, capacity: int = 4):
        self.capacity = capacity
        self.layers: List[str] = []          # list of color IDs, index 0 = bottom

    # ------------------------------------------------------------------
    def is_empty(self) -> bool:
        return len(self.layers) == 0

    def is_full(self) -> bool:
        return len(self.layers) >= self.capacity

    def is_complete(self) -> bool:
        """A tube is complete if it's full and all layers are the same color."""
        return self.is_full() and len(set(self.layers)) == 1

    def top_color(self) -> Optional[str]:
        return self.layers[-1] if self.layers else None

    def free_space(self) -> int:
        return self.capacity - len(self.layers)

    def top_count(self) -> int:
        """How many consecutive same-color layers are at the top."""
        if self.is_empty():
            return 0
        color = self.top_color()
        count = 0
        for layer in reversed(self.layers):
            if layer == color:
                count += 1
            else:
                break
        return count

    def to_dict(self) -> dict:
        return {"capacity": self.capacity, "layers": list(self.layers)}

    @staticmethod
    def from_dict(data: dict) -> "Tube":
        t = Tube(data["capacity"])
        t.layers = data["layers"]
        return t


class GameEngine:
    """
    Manages the complete game state for one session.
    Supports move validation, execution, undo stack, win detection.
    """

    def __init__(self):
        self.tubes: List[Tube] = []
        self.move_count: int = 0
        self.undo_stack: List[List[dict]] = []   # snapshots of tube dicts
        self.move_history: List[Tuple[int, int]] = []
        self.level_config: dict = {}
        self.click_heatmap: Dict[int, int] = {}  # tube_index → click count

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def load_level(self, config: dict):
        """Initialise engine from a level config dict."""
        self.level_config = config
        self.tubes = [Tube.from_dict(t) for t in config["tubes"]]
        self.move_count = 0
        self.undo_stack = []
        self.move_history = []
        self.click_heatmap = {i: 0 for i in range(len(self.tubes))}

    def snapshot(self) -> List[dict]:
        """Return a deep-copyable snapshot of current tube states."""
        return [t.to_dict() for t in self.tubes]

    def restore(self, snap: List[dict]):
        self.tubes = [Tube.from_dict(d) for d in snap]

    def to_dict(self) -> dict:
        return {
            "tubes": self.snapshot(),
            "move_count": self.move_count,
            "level_config": self.level_config,
            "move_history": self.move_history,
            "click_heatmap": self.click_heatmap,
        }

    @staticmethod
    def from_dict(data: dict) -> "GameEngine":
        engine = GameEngine()
        engine.tubes = [Tube.from_dict(t) for t in data["tubes"]]
        engine.move_count = data.get("move_count", 0)
        engine.level_config = data.get("level_config", {})
        engine.move_history = data.get("move_history", [])
        engine.click_heatmap = {int(k): v for k, v in data.get("click_heatmap", {}).items()}
        return engine

    # ------------------------------------------------------------------
    # Move logic
    # ------------------------------------------------------------------

    def can_pour(self, src: int, dst: int) -> Tuple[bool, str]:
        """
        Validate whether pouring from tube src into tube dst is legal.
        Returns (valid: bool, reason: str).
        """
        if src == dst:
            return False, "Same tube"
        if src < 0 or dst < 0 or src >= len(self.tubes) or dst >= len(self.tubes):
            return False, "Invalid tube index"

        s = self.tubes[src]
        d = self.tubes[dst]

        if s.is_empty():
            return False, "Source tube is empty"
        if d.is_full():
            return False, "Destination tube is full"

        # Empty destination → always valid
        if d.is_empty():
            return True, "OK"

        # Colors must match
        if s.top_color() != d.top_color():
            return False, f"Color mismatch ({s.top_color()} vs {d.top_color()})"

        return True, "OK"

    def pour(self, src: int, dst: int) -> Tuple[bool, str, int]:
        """
        Execute a pour move if valid.
        Returns (success, reason, layers_moved).
        """
        valid, reason = self.can_pour(src, dst)
        if not valid:
            return False, reason, 0

        # Save snapshot for undo
        self.undo_stack.append(self.snapshot())

        s = self.tubes[src]
        d = self.tubes[dst]

        color = s.top_color()
        layers_to_move = min(s.top_count(), d.free_space())

        for _ in range(layers_to_move):
            s.layers.pop()
            d.layers.append(color)

        self.move_count += 1
        self.move_history.append((src, dst))
        self.click_heatmap[src] = self.click_heatmap.get(src, 0) + 1

        return True, "OK", layers_to_move

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        snap = self.undo_stack.pop()
        self.restore(snap)
        if self.move_history:
            self.move_history.pop()
        self.move_count = max(0, self.move_count - 1)
        return True

    # ------------------------------------------------------------------
    # Win / lose detection
    # ------------------------------------------------------------------

    def is_won(self) -> bool:
        """All non-empty tubes must be complete (full + uniform color)."""
        for t in self.tubes:
            if t.is_empty():
                continue
            if not t.is_complete():
                return False
        return True

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        moves = []
        n = len(self.tubes)
        for s in range(n):
            for d in range(n):
                valid, _ = self.can_pour(s, d)
                if valid:
                    moves.append((s, d))
        return moves

    def state_hash(self) -> str:
        """Compact string hash of current tube state for BFS visited set."""
        return "|".join(",".join(t.layers) for t in self.tubes)