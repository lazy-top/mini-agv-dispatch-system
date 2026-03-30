import heapq

# 地图的类型：图（Graph），类似于邻接表表示的图
class Graph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node: str):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, a: str, b: str, cost: float = 1.0):
        self.add_node(a)
        self.add_node(b)
        self.adj[a].append((b, cost))
        self.adj[b].append((a, cost))

    def neighbors(self, node: str):
        return self.adj.get(node, [])

    def shortest_path(self, start: str, goal: str):
        pq = [(0, start)]
        dist = {start: 0}
        prev = {}

        while pq:
            cur_dist, cur_node = heapq.heappop(pq)
            if cur_node == goal:
                break

            for nxt, weight in self.neighbors(cur_node):
                nd = cur_dist + weight
                if nxt not in dist or nd < dist[nxt]:
                    dist[nxt] = nd
                    prev[nxt] = cur_node
                    heapq.heappush(pq, (nd, nxt))

        if goal not in dist:
            return [], float("inf")

        path = []
        node = goal
        while node != start:
            path.append(node)
            node = prev[node]
        path.append(start)
        path.reverse()
        return path, dist[goal]