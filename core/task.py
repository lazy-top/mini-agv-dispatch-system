from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKING = "picking"
    DELIVERING = "delivering"
    FINISHED = "finished"


@dataclass
class Task:
    task_id: str
    pickup_node: str
    dropoff_node: str
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    assigned_agv: Optional[str] = None