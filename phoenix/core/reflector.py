from dataclasses import dataclass
@dataclass
class Reflection:
    diagnosis: str
    repair: dict
class Reflector:
    def reflect(self, result, verification):
        if verification.passed: return Reflection("verified", {"action":"preserve_and_record"})
        return Reflection("verification_failure", {"action":"record_failure_and_replan","failures":verification.failures})
