from typing import Dict, List

from core.agv import AGV, AGVStatus
from core.task import Task, TaskStatus
from core.traffic_manager import TrafficManager


class Simulator:
    def __init__(self, agvs: List[AGV], tasks: List[Task], traffic_manager: TrafficManager):
        self.agvs = agvs
        self.tasks = {task.task_id: task for task in tasks}
        self.traffic = traffic_manager
        self.tick_count = 0

        for agv in self.agvs:
            self.traffic.node_occupancy[agv.current_node] = agv.agv_id

    def step(self):
        self.tick_count += 1
        print(f"\n===== TICK {self.tick_count} =====")

        for agv in self.agvs:
            if not agv.path:
                self._handle_arrival(agv)
                continue

            next_node = agv.path[0]
            if self.traffic.can_move(agv.agv_id, agv.current_node, next_node):
                old_node = agv.current_node
                self.traffic.release_node(old_node)
                self.traffic.reserve_move(agv.agv_id, old_node, next_node)

                agv.current_node = next_node
                agv.path.pop(0)

                self.traffic.release_edge(old_node, next_node)
                print(f"{agv.agv_id} moved: {old_node} -> {next_node}")
            else:
                agv.status = AGVStatus.BLOCKED
                print(
                    f"{agv.agv_id} blocked at {agv.current_node}, waiting for {next_node}")

        self.print_status()

    def _handle_arrival(self, agv: AGV):
        if not agv.current_task_id:
            agv.status = AGVStatus.IDLE
            return

        task = self.tasks[agv.current_task_id]

        if agv.current_node == task.pickup_node and task.status == TaskStatus.ASSIGNED:
            task.status = TaskStatus.DELIVERING
            agv.status = AGVStatus.TO_DROPOFF
            print(f"{agv.agv_id} picked task {task.task_id} at {task.pickup_node}")

        elif agv.current_node == task.dropoff_node and task.status == TaskStatus.DELIVERING:
            task.status = TaskStatus.FINISHED
            agv.status = AGVStatus.IDLE
            agv.current_task_id = None
            print(f"{agv.agv_id} finished task {task.task_id} at {task.dropoff_node}")

        else:
            if agv.status == AGVStatus.BLOCKED:
                agv.status = AGVStatus.TO_PICKUP

    def print_status(self):
        for agv in self.agvs:
            print(
                f"[AGV] id={agv.agv_id}, node={agv.current_node}, "
                f"status={agv.status}, task={agv.current_task_id}, path={agv.path}"
            )

        for task in self.tasks.values():
            print(
                f"[TASK] id={task.task_id}, pickup={task.pickup_node}, "
                f"dropoff={task.dropoff_node}, status={task.status}, assigned={task.assigned_agv}"
            )
