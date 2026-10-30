from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json

@dataclass
class LedgerEvent:
    sequence: int
    timestamp: str
    event_type: str
    payload: dict
    previous_hash: str
    hash: str

class Ledger:
    def __init__(self, path="ledger/events.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._read_last_hash()
        self._sequence = self._read_sequence()

    def _read_last_hash(self):
        if not self.path.exists():
            return "0" * 64
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return json.loads(lines[-1])["hash"] if lines else "0" * 64

    def _read_sequence(self):
        return len(self.path.read_text(encoding="utf-8").splitlines()) if self.path.exists() else 0

    @staticmethod
    def _digest(body):
        return hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def append(self, event_type, payload):
        body = {
            "sequence": self._sequence + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": payload,
            "previous_hash": self._last_hash,
        }
        digest = self._digest(body)
        event = LedgerEvent(**body, hash=digest)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), sort_keys=True) + "\n")
        self._sequence += 1
        self._last_hash = digest
        return event

    def verify_chain(self):
        if not self.path.exists():
            return {"valid": True, "events": 0, "error": None}
        previous = "0" * 64
        expected_sequence = 1
        lines = self.path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, 1):
            try:
                event = json.loads(line)
                body = {
                    "sequence": event["sequence"],
                    "timestamp": event["timestamp"],
                    "event_type": event["event_type"],
                    "payload": event["payload"],
                    "previous_hash": event["previous_hash"],
                }
                if event["sequence"] != expected_sequence:
                    return {"valid": False, "events": len(lines), "error": f"sequence_mismatch:{line_number}"}
                if event["previous_hash"] != previous:
                    return {"valid": False, "events": len(lines), "error": f"link_mismatch:{line_number}"}
                if event["hash"] != self._digest(body):
                    return {"valid": False, "events": len(lines), "error": f"hash_mismatch:{line_number}"}
                previous = event["hash"]
                expected_sequence += 1
            except (KeyError, json.JSONDecodeError, TypeError):
                return {"valid": False, "events": len(lines), "error": f"malformed:{line_number}"}
        return {"valid": True, "events": len(lines), "error": None}
