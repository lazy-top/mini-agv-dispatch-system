from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


Position = Tuple[int, int]


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKING = "picking"
    DELIVERING = "delivering"
    FINISHED = "finished"
    FAILED = "failed"


@dataclass(slots=True)
class Task:
    task_id: str
    start: Position
    end: Position
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    assigned_agv: Optional[str] = None

    def assign_agv(self, agv_id: str) -> None:
        self.assigned_agv = agv_id
