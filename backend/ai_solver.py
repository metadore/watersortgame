"""
ai_solver.py
BFS-based optimal solver for Water Sort Puzzle.
Falls back to A* with a heuristic for larger puzzle states.
"""

from collections import deque
import copy
from typing import List, Optional, Tuple, Dict


class SolverState:
    """Immutable snapshot of tube state used in search."""

    def __init__(self, tubes_data: List[dict], path: List[Tuple[int, int]]):
        self.tubes = tubes_data          # list of {"capacity": int, "layers": [str]}
        self.path = path                 # sequence of (src, dst) moves from start

    def key(self) -> str:
        return "|".join(",".join(t["layers"]) for t in self.tubes)

    def is_won(self) -> bool:
        for t in self.tubes:
            if not t["layers"]:
                continue
            cap = t["capacity"]
            layers = t["layers"]
            if len(layers) != cap:
                return False
            if len(set(layers)) != 1:
                return False
        return True

    # ------------------------------------------------------------------ helpers
    def _top_color(self, idx: int) -> Optional[str]:
        layers = self.tubes[idx]["layers"]
        return layers[-1] if layers else None

    def _free_space(self, idx: int) -> int:
        t = self.tubes[idx]
        return t["capacity"] - len(t["layers"])

    def _top_count(self, idx: int) -> int:
        layers = self.tubes[idx]["layers"]
        if not layers:
            return 0
        color = layers[-1]
        count = 0
        for l in reversed(layers):
            if l == color:
                count += 1
            else:
                break
        return count

    def _can_pour(self, src: int, dst: int) -> bool:
        if src == dst:
            return False
        s_layers = self.tubes[src]["layers"]
        d_layers = self.tubes[dst]["layers"]
        if not s_layers:
            return False
        if self._free_space(dst) == 0:
            return False
        if not d_layers:
            return True
        return s_layers[-1] == d_layers[-1]

    def apply_move(self, src: int, dst: int) -> "SolverState":
        """Return new state after pouring src → dst."""
        new_tubes = copy.deepcopy(self.tubes)
        color = new_tubes[src]["layers"][-1]
        layers_to_move = min(self._top_count(src), self._free_space(dst))
        for _ in range(layers_to_move):
            new_tubes[src]["layers"].pop()
            new_tubes[dst]["layers"].append(color)
        return SolverState(new_tubes, self.path + [(src, dst)])

    def legal_moves(self) -> List[Tuple[int, int]]:
        n = len(self.tubes)
        moves = []
        for s in range(n):
            for d in range(n):
                if self._can_pour(s, d):
                    # Prune: don't move between two empty tubes
                    if not self.tubes[s]["layers"]:
                        continue
                    moves.append((s, d))
        return moves

    def heuristic(self) -> int:
        """
        A* heuristic: number of tubes not yet complete.
        Lower → closer to solution.
        """
        count = 0
        for t in self.tubes:
            layers = t["layers"]
            if not layers:
                continue
            if len(layers) != t["capacity"] or len(set(layers)) != 1:
                count += 1
        return count


class AISolver:
    """
    Tries BFS first (guarantees optimal solution for small states).
    Falls back to A* for complex puzzles.
    """

    MAX_BFS_STATES = 200_000

    def solve(self, tubes_data: List[dict]) -> Optional[List[Tuple[int, int]]]:
        start = SolverState(copy.deepcopy(tubes_data), [])

        if start.is_won():
            return []

        # Choose solver based on complexity
        n_tubes = len(tubes_data)
        complexity = n_tubes * max(t["capacity"] for t in tubes_data)

        if complexity <= 24:
            result = self._bfs(start)
        else:
            result = self._astar(start)

        return result

    def _bfs(self, start: SolverState) -> Optional[List[Tuple[int, int]]]:
        queue = deque([start])
        visited: set = {start.key()}
        states_explored = 0

        while queue:
            if states_explored > self.MAX_BFS_STATES:
                # Overflow → fall back to A*
                return self._astar(start)

            state = queue.popleft()
            states_explored += 1

            for src, dst in state.legal_moves():
                next_state = state.apply_move(src, dst)
                key = next_state.key()
                if key in visited:
                    continue
                if next_state.is_won():
                    return next_state.path
                visited.add(key)
                queue.append(next_state)

        return None   # No solution found

    def _astar(self, start: SolverState) -> Optional[List[Tuple[int, int]]]:
        import heapq

        # (f, g, id, state)
        counter = 0
        open_set = [(start.heuristic(), 0, counter, start)]
        visited: Dict[str, int] = {start.key(): 0}

        while open_set:
            f, g, _, state = heapq.heappop(open_set)

            if state.is_won():
                return state.path

            for src, dst in state.legal_moves():
                next_state = state.apply_move(src, dst)
                ng = g + 1
                key = next_state.key()
                if key in visited and visited[key] <= ng:
                    continue
                visited[key] = ng
                counter += 1
                h = next_state.heuristic()
                heapq.heappush(open_set, (ng + h, ng, counter, next_state))

        return None

    def format_solution(self, moves: List[Tuple[int, int]]) -> List[dict]:
        """Convert internal move list to API-friendly format (1-indexed)."""
        return [
            {"step": i + 1, "from_tube": src + 1, "to_tube": dst + 1}
            for i, (src, dst) in enumerate(moves)
        ]