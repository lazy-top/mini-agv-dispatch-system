import heapq
from .base import PathPlanner

class AStar(PathPlanner):
    def __init__(self, grid_map, allow_diagonal=False, heuristic='manhattan'):
        super().__init__(grid_map, allow_diagonal)
        self.heuristic = self._get_heuristic(heuristic)

    def _get_heuristic(self, name):
        if name == 'manhattan':
            return lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1])
        elif name == 'euclidean':
            return lambda a, b: ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5
        else:
            raise ValueError(f"Unknown heuristic: {name}")

    def find_path(self, start, goal):
        if not self.grid_map.get_cell(*start) or not self.grid_map.get_cell(*goal):
            return None

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)

            for neighbor in self._get_neighbors(current):
                # 计算移动代价（直线为1，斜线为√2）
                dr = abs(neighbor[0] - current[0])
                dc = abs(neighbor[1] - current[1])
                if dr == 1 and dc == 1:
                    move_cost = 1.414  # √2
                else:
                    move_cost = 1

                tentative_g = g_score[current] + move_cost
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    @staticmethod
    def _reconstruct_path(came_from, start, goal):
        path = [goal]
        while path[-1] != start:
            path.append(came_from[path[-1]])
        path.reverse()
        return path