from core.graph import Graph


class Planner:
    def __init__(self, graph: Graph):
        self.graph = graph

    def plan(self, start: str, goal: str):
        return self.graph.shortest_path(start, goal)