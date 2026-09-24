import json
from pathlib import Path


class BusStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.journal_path = root / "journal.jsonl"
        self.outbox_path = root / "outbox.jsonl"
        root.mkdir(parents=True, exist_ok=True)

    def _append(self, path: Path, row: dict) -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _read(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(json.loads(line))
        return rows

    def record(self, topic: str, payload: dict) -> None:
        self._append(self.journal_path, {"topic": topic, "payload": payload})

    def recent(self, limit: int = 40) -> list[dict]:
        return list(reversed(self._read(self.journal_path)[-limit:]))

    def enqueue(self, topic: str, payload: dict) -> None:
        self._append(self.outbox_path, {"topic": topic, "payload": payload})

    def pending(self) -> list[dict]:
        return self._read(self.outbox_path)

    def clear_outbox(self) -> None:
        if self.outbox_path.exists():
            self.outbox_path.unlink()
