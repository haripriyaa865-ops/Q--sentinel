from pathlib import Path
import joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.datasets import make_classification
from vqc_assessor import VQCAssessor

MODEL = Path("xgboost_fraud_model.joblib")
FEATURES = ["amount", "hour", "transactions_last_hour", "international"]

def train_demo_model():
    X, y = make_classification(n_samples=2500, n_features=4, n_informative=4,
        n_redundant=0, weights=[0.90, 0.10], random_state=42)
    X[:, 0] = np.clip((X[:, 0] + 3) * 700, 1, 5000)
    X[:, 1] = np.clip(((X[:, 1] + 3) * 4).astype(int), 0, 23)
    X[:, 2] = np.clip(((X[:, 2] + 3) * 2).astype(int), 0, 12)
    X[:, 3] = (X[:, 3] > 0).astype(int)
    model = XGBClassifier(n_estimators=120, max_depth=4, learning_rate=0.06,
        subsample=0.9, colsample_bytree=0.9, eval_metric="logloss", random_state=42)
    model.fit(X, y)
    joblib.dump(model, MODEL)
    return model

class FraudPipeline:
    def __init__(self, confidence_threshold=0.75):
        self.model = joblib.load(MODEL) if MODEL.exists() else train_demo_model()
        self.threshold = confidence_threshold
        self.vqc = VQCAssessor()

    def predict(self, features):
        row = np.array([[float(features[k]) for k in FEATURES]])
        probs = self.model.predict_proba(row)[0]
        fraud = float(probs[1])
        confidence = float(max(probs))
        routed = confidence < self.threshold
        vqc_score = None
        final = fraud
        if routed:
            x = np.array([min(features["amount"]/5000, 1),
                features["hour"]/23,
                min(features["transactions_last_hour"]/12, 1),
                features["international"]], dtype=float)
            vqc_score = self.vqc.score(x)
            final = (fraud + vqc_score) / 2
        return {"primary_fraud_probability": round(fraud, 4),
            "primary_confidence": round(confidence, 4),
            "routed_to_vqc": routed,
            "vqc_fraud_score": None if vqc_score is None else round(vqc_score, 4),
            "final_fraud_score": round(float(final), 4),
            "decision": "BLOCK" if final >= 0.5 else "APPROVE"}
