from dataclasses import dataclass
@dataclass
class Verification:
    passed: bool
    checks: list[str]
    failures: list[str]
    evidence: dict
class Verifier:
    def verify(self, result, checks=None):
        checks = checks or [lambda x: x is not None]; failures=[]
        for i, check in enumerate(checks):
            try:
                if not check(result): failures.append(f"check_{i}")
            except Exception as exc: failures.append(f"check_{i}:{type(exc).__name__}")
        return Verification(not failures,[f"check_{i}" for i in range(len(checks))],failures,{"result_type":type(result).__name__})
