import hashlib, json
from pathlib import Path

class HashChainAudit:
    def __init__(self, path):
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    @staticmethod
    def canonical(obj):
        return json.dumps(obj, sort_keys=True, separators=(",", ":"))

    def append(self, record):
        lines = self.path.read_text(encoding="utf-8").splitlines()
        previous = json.loads(lines[-1])["hash"] if lines else "GENESIS"
        body = {"previous_hash": previous, "record": record}
        digest = hashlib.sha256(self.canonical(body).encode()).hexdigest()
        with self.path.open("a", encoding="utf-8") as f:
            f.write(self.canonical({**body, "hash": digest}) + "\n")
        return digest

    def verify(self):
        previous, count = "GENESIS", 0
        for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                entry = json.loads(line)
                if entry["previous_hash"] != previous:
                    return {"valid": False, "entries_checked": count,
                            "error": f"Previous hash mismatch at line {number}"}
                body = {"previous_hash": previous, "record": entry["record"]}
                expected = hashlib.sha256(self.canonical(body).encode()).hexdigest()
                if entry["hash"] != expected:
                    return {"valid": False, "entries_checked": count,
                            "error": f"Hash mismatch at line {number}"}
                previous, count = entry["hash"], count + 1
            except (KeyError, ValueError, TypeError):
                return {"valid": False, "entries_checked": count,
                        "error": f"Invalid entry at line {number}"}
        return {"valid": True, "entries_checked": count}
