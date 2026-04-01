from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


Position = Tuple[int, int]


class AGVStatus(str, Enum):
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    BLOCKED = "blocked"


class AGV:
    def __init__(self, agv_id, start_pos, map_grid):
        self.id = agv_id
        self.map = map_grid
        self.pos = start_pos          # 当前格子坐标 (r,c)
        self.task = None               # 当前任务对象
        self.path = []                 # 待走路径（不含当前位置）
        self.state = AGVStatus.IDLE            # idle, moving, waiting, blocked
        self.target_pos = None         # 目标位置

    def assign_task(self, target_pos):
        """分配任务，计算路径"""
        path = a_star(self.map, self.pos, target_pos, allow_diagonal=False)
        if path is None:
            print(f"AGV {self.id}: 无法到达目标 {target_pos}")
            return False
        self.task = target_pos
        self.path = path[1:]   # 去掉起点
        self.target_pos = target_pos
        self.state = AGVStatus.MOVING
        return True

    def move_step(self):
        """沿路径移动一步，返回是否到达目标"""
        if self.state != AGVStatus.MOVING or not self.path:
            if self.state == AGVStatus.MOVING and not self.path:
                self.state = AGVStatus.IDLE
                self.task = None
                self.target_pos = None
                print(f"AGV {self.id}: 到达目标")
                return True
            return False

        next_pos = self.path[0]
        # 检查下一格是否被其他 AGV 占用（由调度器外部检查）
        self.pos = next_pos
        self.path.pop(0)
        if not self.path:
            self.state = AGVStatus.IDLE
            self.task = None
            self.target_pos = None
            print(f"AGV {self.id}: 到达目标")
            return True
        return False