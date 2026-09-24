import os
from pathlib import Path

from mimir_bus.client import MimirBus
from mimir_bus.store import BusStore
from mimir_bus.web import serve


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data = Path(os.environ.get("MIMIR_DATA", root / "data"))
    broker = os.environ.get("MIMIR_MQTT_BROKER", "127.0.0.1:1883")
    port = int(os.environ.get("MIMIR_HTTP_PORT", "8090"))
    bus = MimirBus(BusStore(data), broker)
    bus.start()
    print(f"Console MIMIR : http://127.0.0.1:{port}")
    print(f"Broker : {broker}")
    serve(bus, port)


if __name__ == "__main__":
    main()
