from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class AGVStatus(str, Enum):
    IDLE = "idle"
    TO_PICKUP = "to_pickup"
    TO_DROPOFF = "to_dropoff"
    BLOCKED = "blocked"


@dataclass
class AGV:
    agv_id: str
    current_node: str
    status: AGVStatus = AGVStatus.IDLE
    current_task_id: Optional[str] = None
    path: List[str] = field(default_factory=list)
    battery: float = 100.0

    def is_idle(self) -> bool:
        return self.status == AGVStatus.IDLE
