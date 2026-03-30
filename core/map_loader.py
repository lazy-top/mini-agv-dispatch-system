import json
from core.graph import Graph


class MapLoader:
    @staticmethod
    def load_from_json(file_path: str) -> Graph:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph = Graph()

        # 加载节点
        for node in data.get("nodes", []):
            graph.add_node(node)

        # 加载边
        for edge in data.get("edges", []):
            a = edge["from"]
            b = edge["to"]
            cost = edge.get("cost", 1.0)
            graph.add_edge(a, b, cost)

        return graph
