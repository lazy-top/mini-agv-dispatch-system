from typing import Dict, List, Optional

from core.agv import AGV, AGVStatus
from core.task import Task, TaskStatus
from core.planner import Planner


class Dispatcher:
    def __init__(self, planner: Planner):
        self.planner = planner

    def select_best_agv(self, task: Task, agvs: List[AGV]) -> Optional[AGV]:
        idle_agvs = [agv for agv in agvs if agv.is_idle()]
        if not idle_agvs:
            return None

        best_agv = None
        best_cost = float("inf")

        for agv in idle_agvs:
            _, cost = self.planner.plan(agv.current_node, task.pickup_node)
            if cost < best_cost:
                best_cost = cost
                best_agv = agv

        return best_agv

    def assign(self, task: Task, agvs: List[AGV]) -> bool:
        agv = self.select_best_agv(task, agvs)
        if agv is None:
            return False

        path_to_pickup, _ = self.planner.plan(agv.current_node, task.pickup_node)
        path_to_dropoff, _ = self.planner.plan(task.pickup_node, task.dropoff_node)

        full_path = path_to_pickup[:]
        if path_to_dropoff:
            full_path.extend(path_to_dropoff[1:])

        agv.path = full_path[1:] if len(full_path) > 1 else []
        agv.current_task_id = task.task_id
        agv.status = AGVStatus.TO_PICKUP

        task.assigned_agv = agv.agv_id
        task.status = TaskStatus.ASSIGNED
        return True