from core.dispatcher import Dispatcher
from core.grid_map import GridMap
from services import DispatchApplicationService
from ui import ConsoleUI


def build_app() -> DispatchApplicationService:
    grid_map = GridMap(rows=12, cols=20, obstacle_prob=0.18, ensure_connectivity=True, border_free=True, seed=7)
    dispatcher = Dispatcher(grid_map)
    app = DispatchApplicationService(dispatcher)

    app.register_agv("AGV-01", (1, 1))
    app.register_agv("AGV-02", (10, 18))

    app.create_task((2, 2), (9, 15), priority=1)
    app.create_task((9, 2), (2, 17), priority=2)
    app.create_task((1, 10), (10, 10), priority=1)

    return app


def main() -> None:
    app = build_app()
    ui = ConsoleUI(app)
    ui.run(max_steps=80)


if __name__ == "__main__":
    main()
