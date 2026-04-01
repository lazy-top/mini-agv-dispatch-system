from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple

from .agv import AGV, AGVStatus
from .grid_map import GridMap
from .pathfinder import a_star
from .task import Position, Task, TaskStatus


@dataclass(frozen=True, slots=True)
class AGVSnapshot:
    agv_id: str
    position: Position
    status: str
    assigned_task_id: Optional[str]
    remaining_steps: int


@dataclass(frozen=True, slots=True)
class TaskSnapshot:
    task_id: str
    pickup: Position
    dropoff: Position
    priority: int
    status: str
    assigned_agv: Optional[str]


@dataclass(frozen=True, slots=True)
class DispatchSnapshot:
    tick: int
    agvs: Tuple[AGVSnapshot, ...]
    pending_tasks: Tuple[TaskSnapshot, ...]
    active_tasks: Tuple[TaskSnapshot, ...]
    finished_tasks: Tuple[TaskSnapshot, ...]


class Dispatcher:
    """Domain-level scheduler. No I/O and no UI dependencies."""

    def __init__(self, grid_map: GridMap) -> None:
        self._map = grid_map
        self._agvs: Dict[str, AGV] = {}

        self._pending_tasks: Deque[Task] = deque()
        self._tasks: Dict[str, Task] = {}

        self._active_tasks_by_agv: Dict[str, str] = {}
        self._agv_stage: Dict[str, str] = {}

        self._tick = 0

    def register_agv(self, agv: AGV) -> None:
        if agv.agv_id in self._agvs:
            raise ValueError(f"AGV already exists: {agv.agv_id}")
        if not self._map.is_walkable(agv.position):
            raise ValueError(f"AGV position is not walkable: {agv.position}")
        if any(existing.position == agv.position for existing in self._agvs.values()):
            raise ValueError(f"Duplicate AGV start position: {agv.position}")

        self._agvs[agv.agv_id] = agv

    def submit_task(self, task: Task) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"Task already exists: {task.task_id}")
        if not self._map.is_walkable(task.pickup) or not self._map.is_walkable(task.dropoff):
            raise ValueError(
                f"Task contains blocked pickup/dropoff: {task.task_id}")

        self._tasks[task.task_id] = task
        self._pending_tasks.append(task)
        self._sort_pending_tasks()

    def step(self) -> DispatchSnapshot:
        self._tick += 1
        self._allocate_tasks()
        self._move_agvs_one_tick()
        self._post_move_progress()
        return self.snapshot()

    def run(self, max_steps: int = 100) -> DispatchSnapshot:
        for _ in range(max_steps):
            if self._is_all_done():
                break
            self.step()
        return self.snapshot()

    def snapshot(self) -> DispatchSnapshot:
        agv_snapshots = tuple(
            AGVSnapshot(
                agv_id=agv.agv_id,
                position=agv.position,
                status=agv.status.value,
                assigned_task_id=agv.assigned_task_id,
                remaining_steps=len(agv.route),
            )
            for agv in sorted(self._agvs.values(), key=lambda item: item.agv_id)
        )

        pending = tuple(
            self._to_task_snapshot(task)
            for task in sorted(self._pending_tasks, key=lambda item: (item.priority, item.task_id))
        )
        active = tuple(
            self._to_task_snapshot(task)
            for task in sorted(
                (task for task in self._tasks.values() if task.status in {
                 TaskStatus.PICKING, TaskStatus.DELIVERING}),
                key=lambda item: item.task_id,
            )
        )
        finished = tuple(
            self._to_task_snapshot(task)
            for task in sorted(
                (task for task in self._tasks.values()
                 if task.status == TaskStatus.FINISHED),
                key=lambda item: item.task_id,
            )
        )

        return DispatchSnapshot(
            tick=self._tick,
            agvs=agv_snapshots,
            pending_tasks=pending,
            active_tasks=active,
            finished_tasks=finished,
        )

    def render_map(self) -> str:
        occupied_positions = [agv.position for agv in self._agvs.values()]
        return self._map.render_ascii(occupied_positions)

    def _to_task_snapshot(self, task: Task) -> TaskSnapshot:
        return TaskSnapshot(
            task_id=task.task_id,
            pickup=task.pickup,
            dropoff=task.dropoff,
            priority=task.priority,
            status=task.status.value,
            assigned_agv=task.assigned_agv,
        )

    def _sort_pending_tasks(self) -> None:
        sorted_pending = sorted(self._pending_tasks,
                                key=lambda item: (item.priority, item.task_id))
        self._pending_tasks = deque(sorted_pending)

    def _allocate_tasks(self) -> None:
        if not self._pending_tasks:
            return

        idle_agvs = [agv for agv in self._agvs.values(
        ) if agv.status == AGVStatus.IDLE and not agv.assigned_task_id]
        idle_agvs.sort(key=lambda item: item.agv_id)

        while idle_agvs and self._pending_tasks:
            agv = idle_agvs.pop(0)
            task = self._pending_tasks.popleft()

            if not self._assign_task_to_agv(agv, task):
                task.status = TaskStatus.FAILED
                task.assigned_agv = None

    def _assign_task_to_agv(self, agv: AGV, task: Task) -> bool:
        route_to_pickup = a_star(self._map, agv.position, task.pickup)
        if route_to_pickup is None:
            return False

        task.assigned_agv = agv.agv_id
        task.status = TaskStatus.ASSIGNED
        agv.assigned_task_id = task.task_id
        self._active_tasks_by_agv[agv.agv_id] = task.task_id

        if agv.position == task.pickup:
            task.status = TaskStatus.DELIVERING
            self._agv_stage[agv.agv_id] = "to_dropoff"
            route_to_dropoff = a_star(self._map, agv.position, task.dropoff)
            if route_to_dropoff is None:
                agv.mark_blocked()
                task.status = TaskStatus.FAILED
                agv.release_task()
                self._active_tasks_by_agv.pop(agv.agv_id, None)
                self._agv_stage.pop(agv.agv_id, None)
                return False
            agv.set_route(route_to_dropoff[1:])
        else:
            task.status = TaskStatus.PICKING
            self._agv_stage[agv.agv_id] = "to_pickup"
            agv.set_route(route_to_pickup[1:])

        self._post_move_progress_for_agv(agv)
        return True

    def _move_agvs_one_tick(self) -> None:
        current_positions = {agv.position for agv in self._agvs.values()}
        reserved_next_positions: set[Position] = set()

        candidates = [agv for agv in self._agvs.values() if agv.route]
        candidates.sort(key=lambda item: item.agv_id)

        for agv in candidates:
            next_pos = agv.next_position()
            if next_pos is None:
                continue

            occupied_by_other = next_pos in current_positions and next_pos != agv.position
            if occupied_by_other or next_pos in reserved_next_positions:
                agv.mark_waiting()
                continue

            current_positions.discard(agv.position)
            agv.move_one_step()
            current_positions.add(agv.position)
            reserved_next_positions.add(agv.position)

            if agv.route:
                agv.mark_moving()

    def _post_move_progress(self) -> None:
        for agv in self._agvs.values():
            self._post_move_progress_for_agv(agv)

    def _post_move_progress_for_agv(self, agv: AGV) -> None:
        task_id = self._active_tasks_by_agv.get(agv.agv_id)
        if not task_id:
            if not agv.route and agv.status != AGVStatus.BLOCKED:
                agv.status = AGVStatus.IDLE
            return

        task = self._tasks[task_id]
        stage = self._agv_stage.get(agv.agv_id)

        if stage == "to_pickup" and not agv.route:
            route_to_dropoff = a_star(self._map, agv.position, task.dropoff)
            if route_to_dropoff is None:
                task.status = TaskStatus.FAILED
                agv.mark_blocked()
                self._release_active_task(agv)
                return

            task.status = TaskStatus.DELIVERING
            self._agv_stage[agv.agv_id] = "to_dropoff"
            agv.set_route(route_to_dropoff[1:])
            stage = "to_dropoff"

        if stage == "to_dropoff" and not agv.route:
            task.status = TaskStatus.FINISHED
            self._release_active_task(agv)

    def _release_active_task(self, agv: AGV) -> None:
        self._active_tasks_by_agv.pop(agv.agv_id, None)
        self._agv_stage.pop(agv.agv_id, None)
        agv.release_task()

    def _is_all_done(self) -> bool:
        if self._pending_tasks:
            return False
        if any(task.status in {TaskStatus.PICKING, TaskStatus.DELIVERING, TaskStatus.ASSIGNED} for task in self._tasks.values()):
            return False
        return all(not agv.route and agv.status in {AGVStatus.IDLE, AGVStatus.BLOCKED} for agv in self._agvs.values())
