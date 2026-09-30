import json
import tempfile
from pathlib import Path

from phoenix.core.agent import PhoenixBot
from phoenix.core.executor import Executor, Tool
from phoenix.core.ledger import Ledger


def test_cycle_verifies_and_records():
    with tempfile.TemporaryDirectory() as d:
        bot = PhoenixBot(str(Path(d) / "events.jsonl"))
        result = bot.run("hello")
        assert result.verified is True
        assert result.result == "hello"
        assert len(Path(d, "events.jsonl").read_text().splitlines()) == 3
        assert bot.ledger.verify_chain()["valid"] is True


def test_permission_gate_blocks_side_effects():
    executor = Executor()
    executor.register(Tool("danger", lambda: "ran", side_effect=True, permission="write"))
    try:
        executor.execute("danger", {}, set())
        assert False, "side effect should require permission"
    except PermissionError:
        pass
    assert executor.execute("danger", {}, {"write"}) == "ran"


def test_ledger_detects_tampering():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "events.jsonl"
        ledger = Ledger(str(path))
        ledger.append("input", {"x": 1})
        ledger.append("result", {"x": 2})
        assert ledger.verify_chain()["valid"] is True
        rows = path.read_text().splitlines()
        rows[1] = rows[1].replace('"x": 2', '"x": 999', 1)
        path.write_text("\n".join(rows) + "\n")
        assert ledger.verify_chain()["valid"] is False


def test_failed_execution_is_preserved_and_not_promoted():
    with tempfile.TemporaryDirectory() as d:
        bot = PhoenixBot(str(Path(d) / "events.jsonl"))
        bot.executor.register(Tool("fail", lambda: (_ for _ in ()).throw(RuntimeError("boom"))))
        bot.reason = lambda request: {"intent": request, "action": "fail", "args": {}}
        result = bot.run("trigger failure")
        assert result.verified is False
        assert result.result is None
        events = [json.loads(line) for line in Path(d, "events.jsonl").read_text().splitlines()]
        assert any(e["event_type"] == "execution_error" for e in events)
        assert bot.ledger.verify_chain()["valid"] is True


def test_sequential_stress_1000_cycles():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "events.jsonl"
        bot = PhoenixBot(str(path))
        for i in range(1000):
            result = bot.run(f"stress-{i}")
            assert result.verified is True
            assert result.result == f"stress-{i}"
        assert len(path.read_text().splitlines()) == 3000
        audit = bot.ledger.verify_chain()
        assert audit == {"valid": True, "events": 3000, "error": None}
