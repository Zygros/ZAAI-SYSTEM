from dataclasses import dataclass, asdict
import json
from .memory import Memory
from .executor import Executor, Tool
from .verifier import Verifier
from .reflector import Reflector
from .ledger import Ledger
@dataclass
class AgentResult:
    request:str; plan:dict; result:object; verified:bool; reflection:dict; ledger_hash:str
    def to_json(self): return json.dumps(asdict(self),indent=2,default=str)
class PhoenixBot:
    def __init__(self,ledger_path="ledger/events.jsonl"):
        self.memory=Memory(); self.executor=Executor(); self.verifier=Verifier(); self.reflector=Reflector(); self.ledger=Ledger(ledger_path); self.executor.register(Tool("echo",lambda text:text))
    def reason(self,request): return {"intent":request,"action":"echo","args":{"text":request}}
    def run(self,request):
        plan=self.reason(request); self.ledger.append("input",{"request":request}); self.ledger.append("plan",plan)
        try: result=self.executor.execute(plan["action"],plan["args"],set()); verification=self.verifier.verify(result)
        except Exception as exc: result=None; verification=self.verifier.verify(result,[lambda _:False]); self.ledger.append("execution_error",{"type":type(exc).__name__,"message":str(exc)})
        reflection=self.reflector.reflect(result,verification); event=self.ledger.append("cycle",{"verified":verification.passed,"reflection":asdict(reflection)}); self.memory.remember({"state":{"last_request":request,"last_verified":verification.passed},"result":result})
        return AgentResult(request,plan,result,verification.passed,asdict(reflection),event.hash)
