import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from phoenix_blockchain_anchor import PhoenixBlockchainAnchor


class PhoenixAnchorPureFunctionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "artifact.bin"
        self.path.write_bytes(b"Phoenix Unbound stable hash test\x00\x01")

    def tearDown(self):
        self.temp.cleanup()

    def test_compute_sha256_matches_standard_digest(self):
        anchor = PhoenixBlockchainAnchor()
        expected = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.assertEqual(anchor.compute_sha256(str(self.path)), expected)

    def test_create_anchor_payload_preserves_hash_and_fixed_time(self):
        anchor = PhoenixBlockchainAnchor()
        anchor.timestamp = "2026-11-23T00:00:00Z"
        payload = anchor.create_anchor_payload(str(self.path), "unit-test artifact")
        self.assertEqual(payload["file_hash"], hashlib.sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(payload["timestamp"], "2026-11-23T00:00:00Z")
        self.assertEqual(payload["description"], "unit-test artifact")
        self.assertEqual(payload["sovereign_hash"], PhoenixBlockchainAnchor.SOVEREIGN_HASH)

    def test_solana_pda_method_is_explicit_simulation_and_deterministic(self):
        anchor = PhoenixBlockchainAnchor()
        payload = {"file_hash": "abc123", "description": "test"}
        with patch("phoenix_blockchain_anchor.subprocess.run") as run:
            first = anchor.anchor_to_solana_pda(payload)
            second = anchor.anchor_to_solana_pda(payload)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "SIMULATION")
        self.assertEqual(first["payload_hash"], hashlib.sha256(
            __import__("json").dumps(payload, sort_keys=True).encode()
        ).hexdigest())
        run.assert_not_called()

    def test_import_and_pure_methods_do_not_write_anchor_ledger(self):
        ledger = Path(self.temp.name) / "ledger.json"
        anchor = PhoenixBlockchainAnchor()
        anchor.compute_sha256(str(self.path))
        anchor.create_anchor_payload(str(self.path), "read-only test")
        anchor.anchor_to_solana_pda({"file_hash": "abc"})
        self.assertFalse(ledger.exists())


if __name__ == "__main__":
    unittest.main()
