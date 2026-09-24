import json
import threading
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from mimir_bus.alerts import EIR_TOPICS, TOPIC_INFIRMARY
from mimir_bus.store import BusStore


class MimirBus:
    def __init__(self, store: BusStore, broker: str) -> None:
        parsed = urlparse(broker if "://" in broker else f"mqtt://{broker}")
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 1883
        self.store = store
        self.connected = False
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="mimir-bus")
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._lock = threading.Lock()

    def start(self) -> None:
        self._client.connect_async(self.host, self.port, keepalive=30)
        self._client.loop_start()

    def stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def publish_infirmary(self, payload: dict) -> bool:
        return self._publish(TOPIC_INFIRMARY, payload)

    def _publish(self, topic: str, payload: dict) -> bool:
        encoded = json.dumps(payload, ensure_ascii=False)
        with self._lock:
            if not self.connected:
                self.store.enqueue(topic, payload)
                return False
            result = self._client.publish(topic, encoded, qos=1)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            self.store.enqueue(topic, payload)
            return False
        self.store.record(topic, payload)
        return True

    def _flush(self) -> None:
        pending = self.store.pending()
        if not pending:
            return
        self.store.clear_outbox()
        for row in pending:
            self._publish(row["topic"], row["payload"])

    def _on_connect(self, client, userdata, flags, rc) -> None:
        self.connected = rc == 0
        if not self.connected:
            return
        for topic in EIR_TOPICS:
            client.subscribe(topic, qos=1)
        self._flush()

    def _on_disconnect(self, client, userdata, rc) -> None:
        self.connected = False

    def _on_message(self, client, userdata, msg) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {"raw": msg.payload.decode("utf-8", errors="replace")}
        if not isinstance(payload, dict):
            payload = {"raw": payload}
        self.store.record(msg.topic, payload)
