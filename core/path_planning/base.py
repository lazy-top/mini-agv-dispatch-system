from abc import ABC, abstractmethod

class PathPlanner(ABC):
    """路径规划算法基类"""
    def __init__(self, grid_map, allow_diagonal=False):
        self.grid_map = grid_map
        self.allow_diagonal = allow_diagonal
        self.rows, self.cols = grid_map.get_size()

    @abstractmethod
    def find_path(self, start, goal):
        """
        查找路径
        :param start: 起点坐标 (row, col)
        :param goal: 终点坐标 (row, col)
        :return: 路径列表（包含起点和终点），若不可达返回 None
        """
        pass

    def _get_neighbors(self, node):
        """根据 allow_diagonal 获取相邻节点"""
        r, c = node
        if self.allow_diagonal:
            dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        else:
            dirs = [(-1,0),(1,0),(0,-1),(0,1)]

        neighbors = []
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.grid_map.get_cell(nr, nc) == 1:
                    neighbors.append((nr, nc))
        return neighbors