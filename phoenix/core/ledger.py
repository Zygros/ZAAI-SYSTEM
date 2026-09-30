from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
@dataclass
class LedgerEvent:
    sequence:int; timestamp:str; event_type:str; payload:dict; previous_hash:str; hash:str
class Ledger:
    def __init__(self,path="ledger/events.jsonl"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._last_hash=self._read_last_hash(); self._sequence=self._read_sequence()
    def _read_last_hash(self):
        if not self.path.exists(): return "0"*64
        lines=self.path.read_text().splitlines(); return json.loads(lines[-1])["hash"] if lines else "0"*64
    def _read_sequence(self): return len(self.path.read_text().splitlines()) if self.path.exists() else 0
    def append(self,event_type,payload):
        body={"sequence":self._sequence+1,"timestamp":datetime.now(timezone.utc).isoformat(),"event_type":event_type,"payload":payload,"previous_hash":self._last_hash}
        digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest(); event=LedgerEvent(**body,hash=digest)
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(asdict(event),sort_keys=True)+"\n")
        self._sequence+=1; self._last_hash=digest; return event
