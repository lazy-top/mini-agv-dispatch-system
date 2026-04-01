from collections import deque
from .base import PathPlanner

class BFS(PathPlanner):
    def find_path(self, start, goal):
        if not self.grid_map.get_cell(*start) or not self.grid_map.get_cell(*goal):
            return None

        queue = deque([start])
        came_from = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)

            for neighbor in self._get_neighbors(current):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return None

    @staticmethod
    def _reconstruct_path(came_from, start, goal):
        path = [goal]
        while path[-1] != start:
            path.append(came_from[path[-1]])
        path.reverse()
        return path