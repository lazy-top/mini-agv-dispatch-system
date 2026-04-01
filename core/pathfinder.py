from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

from .grid_map import GridMap


Position = Tuple[int, int]


def _manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(grid_map: GridMap, start: Position, goal: Position) -> Optional[List[Position]]:
    """Return path from start to goal (inclusive), or None when unreachable."""
    if not grid_map.is_walkable(start) or not grid_map.is_walkable(goal):
        return None

    open_heap: List[Tuple[int, Position]] = []
    heapq.heappush(open_heap, (0, start))

    came_from: Dict[Position, Position] = {}
    g_score: Dict[Position, int] = {start: 0}
    f_score: Dict[Position, int] = {start: _manhattan(start, goal)}

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal:
            return _reconstruct_path(came_from, current)

        current_g = g_score[current]
        for neighbor in grid_map.neighbors(current):
            tentative_g = current_g + 1
            if tentative_g >= g_score.get(neighbor, 10**9):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            estimate = tentative_g + _manhattan(neighbor, goal)
            f_score[neighbor] = estimate
            heapq.heappush(open_heap, (estimate, neighbor))

    return None


def _reconstruct_path(came_from: Dict[Position, Position], current: Position) -> List[Position]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
