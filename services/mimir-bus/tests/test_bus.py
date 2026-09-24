import tempfile
import unittest
from pathlib import Path

from mimir_bus.alerts import infirmary_payload
from mimir_bus.store import BusStore
from mimir_bus.web import Console


class StoreTests(unittest.TestCase):
    def test_journal_and_outbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = BusStore(Path(tmp))
            store.record("yggdrasil/eir/stock/low", {"drug_id": "paracetamol", "remaining_units": 0})
            store.enqueue("yggdrasil/mimir/security/infirmary", {"alert": "wan_down"})
            self.assertEqual(store.recent()[0]["payload"]["drug_id"], "paracetamol")
            self.assertEqual(len(store.pending()), 1)
            store.clear_outbox()
            self.assertEqual(store.pending(), [])

    def test_unknown_alert_rejected(self) -> None:
        with self.assertRaises(ValueError):
            infirmary_payload("exploit")

    def test_alert_payload_has_no_clinical_field(self) -> None:
        payload = infirmary_payload("suricata_match", drug_id="para cetamol!")
        self.assertEqual(payload["alert"], "suricata_match")
        self.assertNotIn("symptom", payload)
        self.assertEqual(payload["drug_id"], "paracetamol")

    def test_console_queues_when_broker_down(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = BusStore(Path(tmp))

            class Offline:
                connected = False
                store = None

                def publish_infirmary(self, payload):
                    self.store.enqueue("yggdrasil/mimir/security/infirmary", payload)
                    return False

            offline = Offline()
            offline.store = store
            console = Console(offline)
            result = console.publish("wan_down")
            self.assertTrue(result["queued"])
            self.assertEqual(console.state()["pending"], 1)


if __name__ == "__main__":
    unittest.main()
