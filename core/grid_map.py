from __future__ import annotations

import random
from collections import deque
from typing import Iterable, List, Tuple


Position = Tuple[int, int]


class GridMap:
    """Grid map with walkable cells (1) and obstacles (0)."""

    def __init__(
        self,
        rows: int,
        cols: int,
        obstacle_prob: float = 0.2,
        ensure_connectivity: bool = True,
        border_free: bool = True,
        seed: int | None = None,
    ) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive")
        if not 0 <= obstacle_prob < 1:
            raise ValueError("obstacle_prob must be in [0, 1)")

        self.rows = rows
        self.cols = cols
        self.obstacle_prob = obstacle_prob
        self.ensure_connectivity = ensure_connectivity
        self.border_free = border_free
        self._rng = random.Random(seed)
        self.grid: List[List[int]] = []

        self.generate()

    def generate(self) -> None:
        if not self.ensure_connectivity:
            self._generate_simple()
            return

        while True:
            self._generate_simple()
            if self.is_connected():
                return

    def _generate_simple(self) -> None:
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                if self.border_free and (r in {0, self.rows - 1} or c in {0, self.cols - 1}):
                    self.grid[r][c] = 1
                    continue
                if self._rng.random() < self.obstacle_prob:
                    self.grid[r][c] = 0

    def in_bounds(self, pos: Position) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, pos: Position) -> bool:
        if not self.in_bounds(pos):
            return False
        r, c = pos
        return self.grid[r][c] == 1

    def neighbors(self, pos: Position) -> List[Position]:
        r, c = pos
        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [candidate for candidate in candidates if self.is_walkable(candidate)]

    def set_cell(self, pos: Position, value: int) -> None:
        if value not in (0, 1):
            raise ValueError("cell value must be 0 or 1")
        if not self.in_bounds(pos):
            raise IndexError("position out of range")

        r, c = pos
        self.grid[r][c] = value

    def to_matrix(self) -> List[List[int]]:
        return [row[:] for row in self.grid]

    def get_free_cells(self) -> List[Position]:
        return [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c] == 1
        ]

    def is_connected(self) -> bool:
        free_cells = self.get_free_cells()
        if not free_cells:
            return False

        visited: set[Position] = set()
        queue = deque([free_cells[0]])

        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            for nxt in self.neighbors(cur):
                if nxt not in visited:
                    queue.append(nxt)

        return len(visited) == len(free_cells)

    def render_ascii(self, occupied: Iterable[Position] | None = None) -> str:
        occupied_set = set(occupied or [])
        lines: List[str] = []
        for r in range(self.rows):
            chars: List[str] = []
            for c in range(self.cols):
                pos = (r, c)
                if pos in occupied_set:
                    chars.append("A")
                elif self.grid[r][c] == 0:
                    chars.append("#")
                else:
                    chars.append(".")
            lines.append("".join(chars))
        return "\n".join(lines)
