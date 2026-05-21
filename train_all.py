"""
Run this once to train and save all models.
"""

import subprocess
import sys

steps = [
    ("Generating dataset", "data/raw/generate_data.py"),
    ("Preprocessing data", "src/preprocessing.py"),
    ("Training XGBoost risk model", "src/models/risk_model.py"),
    ("Training LSTM forecaster", "src/models/lstm_model.py"),
    ("Testing SHAP explainer", "src/explainability/shap_explainer.py"),
]

for label, script in steps:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")

    result = subprocess.run([sys.executable, script])

    if result.returncode != 0:
        print(f"\n❌ ERROR in: {script}")
        sys.exit(1)

print("\n\n✅ All models trained and saved to models/")
print("Now run:")
print("  uvicorn api.main:app --reload --port 8000")
print("  streamlit run dashboard/app.py")