# Q-SENTINEL
### AI-Driven Multi-Stage Financial Transaction Security

Educational prototype showing a staged fraud-risk workflow:
1. ESP32 + RC522 sends a demo card-scan reference to a Python API.
2. XGBoost estimates primary fraud risk.
3. Low-confidence cases are routed to a secondary assessment.
4. An optional PennyLane variational quantum circuit (VQC) produces a demo score.
5. A SHA-256 hash chain records decisions and supports local integrity checks.

## Important limitations
- This is a demonstration prototype, not a banking/payment authorization system.
- The XGBoost model is trained on generated synthetic data, not real transactions.
- VQC parameters are fixed and untrained. No quantum advantage is claimed.
- If PennyLane is missing, the secondary score is a heuristic, not a quantum result.
- Card UID is not authentication. Do not send real card/account information.
- The local hash chain is not a distributed blockchain and is not tamper-proof against full log replacement.

## Run backend (Python 3.10+)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python train_model.py
python app.py
```
API: `http://127.0.0.1:5000`

## Test API
```bash
curl -X POST http://127.0.0.1:5000/analyze -H "Content-Type: application/json" -d "{\"card_uid\":\"DEMO1234\"}"
curl http://127.0.0.1:5000/audit/verify
```

## Hardware
See `firmware/esp32_rc522.ino`. Update Wi-Fi credentials and the PC's local IP.
ESP32 and PC must be on the same trusted local network. Do not expose this demo server publicly.

## Future improvements
Use a documented real dataset, proper train/validation/test splits, report precision/recall/F1/ROC-AUC, train and evaluate the VQC, and add authentication and encrypted transport before any real deployment.
