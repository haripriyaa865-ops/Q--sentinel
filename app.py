from flask import Flask, request, jsonify
from model_pipeline import FraudPipeline
from audit import HashChainAudit
import hashlib, time

app = Flask(__name__)
pipeline = FraudPipeline()
audit = HashChainAudit("audit_log.jsonl")

def demo_features(card_uid):
    digest = hashlib.sha256(card_uid.encode()).digest()
    return {
        "amount": float(10 + int.from_bytes(digest[:2], "big") % 4990),
        "hour": int(digest[2] % 24),
        "transactions_last_hour": int(digest[3] % 12),
        "international": int(digest[4] % 2),
    }

@app.get("/")
def home():
    return jsonify({"project": "Q-SENTINEL", "status": "demo API running",
                    "warning": "Educational prototype only. Not for real payment decisions."})

@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    uid = str(data.get("card_uid", "")).strip()
    if not uid:
        return jsonify({"error": "card_uid is required"}), 400
    features = demo_features(uid)
    result = pipeline.predict(features)
    record = {"timestamp": time.time(),
              "card_reference": hashlib.sha256(uid.encode()).hexdigest()[:12],
              "features": features, **result}
    record["audit_hash"] = audit.append(record)
    return jsonify(record)

@app.get("/audit/verify")
def verify():
    return jsonify(audit.verify())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
