from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.agv import AGV
from core.dispatcher import DispatchSnapshot, Dispatcher
from core.task import Position, Task


@dataclass(slots=True)
class AppConfig:
    max_steps: int = 200


class DispatchApplicationService:
    """Application facade used by UI/API layers."""

    def __init__(self, dispatcher: Dispatcher, config: Optional[AppConfig] = None) -> None:
        self._dispatcher = dispatcher
        self._config = config or AppConfig()
        self._task_seq = 0

    def register_agv(self, agv_id: str, start_pos: Position) -> None:
        self._dispatcher.register_agv(AGV(agv_id=agv_id, position=start_pos))

    def create_task(self, pickup: Position, dropoff: Position, priority: int = 1) -> str:
        self._task_seq += 1
        task_id = f"T{self._task_seq:04d}"
        task = Task(task_id=task_id, pickup=pickup, dropoff=dropoff, priority=priority)
        self._dispatcher.submit_task(task)
        return task_id

    def step(self) -> DispatchSnapshot:
        return self._dispatcher.step()

    def run(self, max_steps: Optional[int] = None) -> DispatchSnapshot:
        return self._dispatcher.run(max_steps=max_steps or self._config.max_steps)

    def snapshot(self) -> DispatchSnapshot:
        return self._dispatcher.snapshot()

    def render_map(self) -> str:
        return self._dispatcher.render_map()
