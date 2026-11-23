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

    def test_pure_methods_do_not_open_any_file_for_writing(self):
        anchor = PhoenixBlockchainAnchor()
        with patch("builtins.open", wraps=open) as open_mock:
            anchor.compute_sha256(str(self.path))
            anchor.create_anchor_payload(str(self.path), "read-only test")
            anchor.anchor_to_solana_pda({"file_hash": "abc"})
        write_modes = [
            call.args[1] if len(call.args) > 1 else call.kwargs.get("mode", "r")
            for call in open_mock.call_args_list
            if any(flag in (call.args[1] if len(call.args) > 1 else call.kwargs.get("mode", "r"))
                   for flag in ("w", "a", "x", "+"))
        ]
        self.assertEqual(write_modes, [])


if __name__ == "__main__":
    unittest.main()
