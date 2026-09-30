import tempfile
from pathlib import Path
from phoenix.core.agent import PhoenixBot

def test_cycle_verifies_and_records():
    with tempfile.TemporaryDirectory() as d:
        bot=PhoenixBot(str(Path(d)/"events.jsonl")); result=bot.run("hello")
        assert result.verified is True
        assert result.result == "hello"
        assert len(Path(d,"events.jsonl").read_text().splitlines()) == 3
