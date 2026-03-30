class TrafficManager:
    def __init__(self):
        self.node_occupancy = {}
        self.edge_occupancy = {}

    def can_move(self, agv_id: str, current_node: str, next_node: str) -> bool:
        edge_key = tuple(sorted((current_node, next_node)))
        occupied_by = self.edge_occupancy.get(edge_key)
        if occupied_by is not None and occupied_by != agv_id:
            return False

        node_occupied_by = self.node_occupancy.get(next_node)
        if node_occupied_by is not None and node_occupied_by != agv_id:
            return False

        return True

    def reserve_move(self, agv_id: str, current_node: str, next_node: str):
        edge_key = tuple(sorted((current_node, next_node)))
        self.edge_occupancy[edge_key] = agv_id
        self.node_occupancy[next_node] = agv_id

    def release_node(self, node: str):
        if node in self.node_occupancy:
            del self.node_occupancy[node]

    def release_edge(self, current_node: str, next_node: str):
        edge_key = tuple(sorted((current_node, next_node)))
        if edge_key in self.edge_occupancy:
            del self.edge_occupancy[edge_key]