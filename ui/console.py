from __future__ import annotations

from typing import Protocol

from core.dispatcher import DispatchSnapshot


class DispatchBackend(Protocol):
    def step(self) -> DispatchSnapshot: ...

    def snapshot(self) -> DispatchSnapshot: ...

    def render_map(self) -> str: ...


class ConsoleUI:
    """Console adapter that depends on a backend protocol, not core internals."""

    def __init__(self, backend: DispatchBackend) -> None:
        self._backend = backend

    def render(self, snapshot: DispatchSnapshot) -> str:
        lines: list[str] = []
        lines.append(f"Tick: {snapshot.tick}")
        lines.append("Map:")
        lines.append(self._backend.render_map())
        lines.append("AGVs:")

        for agv in snapshot.agvs:
            lines.append(
                f"  - {agv.agv_id} pos={agv.position} status={agv.status} task={agv.assigned_task_id} steps={agv.remaining_steps}"
            )

        lines.append(
            f"Tasks: pending={len(snapshot.pending_tasks)} active={len(snapshot.active_tasks)} finished={len(snapshot.finished_tasks)}"
        )
        return "\n".join(lines)

    def run(self, max_steps: int = 50) -> None:
        print(self.render(self._backend.snapshot()))
        for _ in range(max_steps):
            snapshot = self._backend.step()
            print("-" * 60)
            print(self.render(snapshot))
            if not snapshot.pending_tasks and not snapshot.active_tasks:
                break
