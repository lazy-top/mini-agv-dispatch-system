import heapq
from .base import PathPlanner

class Dijkstra(PathPlanner):
    def find_path(self, start, goal):
        if not self.grid_map.get_cell(*start) or not self.grid_map.get_cell(*goal):
            return None

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        dist = {start: 0}

        while open_set:
            cost, current = heapq.heappop(open_set)
            if current == goal:
                return self._reconstruct_path(came_from, start, goal)

            for neighbor in self._get_neighbors(current):
                # 移动代价（直线为1，斜线为√2）
                dr = abs(neighbor[0] - current[0])
                dc = abs(neighbor[1] - current[1])
                if dr == 1 and dc == 1:
                    move_cost = 1.414
                else:
                    move_cost = 1

                new_cost = cost + move_cost
                if neighbor not in dist or new_cost < dist[neighbor]:
                    dist[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(open_set, (new_cost, neighbor))

        return None

    @staticmethod
    def _reconstruct_path(came_from, start, goal):
        path = [goal]
        while path[-1] != start:
            path.append(came_from[path[-1]])
        path.reverse()
        return path