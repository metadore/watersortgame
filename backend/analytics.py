"""
analytics.py
Tracks per-session analytics: time, moves, undo usage, heatmap, failed attempts.
"""

import time
from typing import Dict, List, Optional


class Analytics:
    """Per-session analytics recorder."""

    def __init__(self):
        self.sessions: Dict[str, dict] = {}   # session_id → data

    # ------------------------------------------------------------------ session
    def start_session(self, session_id: str, level: int):
        self.sessions[session_id] = {
            "session_id": session_id,
            "level": level,
            "start_time": time.time(),
            "end_time": None,
            "time_taken": None,
            "moves": 0,
            "undo_count": 0,
            "failed_attempts": 0,
            "won": False,
            "heatmap": {},
        }

    def record_move(self, session_id: str, src: int, dst: int):
        s = self._get(session_id)
        if s:
            s["moves"] += 1
            s["heatmap"][str(src)] = s["heatmap"].get(str(src), 0) + 1

    def record_undo(self, session_id: str):
        s = self._get(session_id)
        if s:
            s["undo_count"] += 1

    def record_failed_attempt(self, session_id: str):
        s = self._get(session_id)
        if s:
            s["failed_attempts"] += 1

    def record_win(self, session_id: str):
        s = self._get(session_id)
        if s:
            s["end_time"] = time.time()
            s["time_taken"] = s["end_time"] - s["start_time"]
            s["won"] = True

    def get_session(self, session_id: str) -> Optional[dict]:
        return self.sessions.get(session_id)

    def get_all(self) -> List[dict]:
        return list(self.sessions.values())

    def summary(self) -> dict:
        all_s = self.get_all()
        won = [s for s in all_s if s["won"]]
        return {
            "total_sessions": len(all_s),
            "total_wins": len(won),
            "avg_moves": sum(s["moves"] for s in won) / max(len(won), 1),
            "avg_time": sum(s["time_taken"] or 0 for s in won) / max(len(won), 1),
            "total_undos": sum(s["undo_count"] for s in all_s),
            "sessions": all_s,
        }

    def _get(self, session_id: str) -> Optional[dict]:
        return self.sessions.get(session_id)