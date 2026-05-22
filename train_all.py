
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
        print(f"\nERROR in: {script}")
        sys.exit(1)

print("\n\nAll models trained and saved to models/")