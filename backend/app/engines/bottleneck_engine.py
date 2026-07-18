from app.engines.base import BaseEngine
from app.engines.capacity_engine import CapacityEngine


class BottleneckEngine(BaseEngine):
    name = "bottleneck_engine"

    def execute(self, db, factory_id: int):
        cap = CapacityEngine().execute(db, factory_id)
        lines = cap.data.get("lines", [])
        ranked = sorted(lines, key=lambda x: x["utilization"], reverse=True)
        top = ranked[:3] if ranked else []
        return self._ok("Bottleneck analysis complete",
                        {"bottlenecks": top, "most_constrained": top[0]["line"] if top else None})
