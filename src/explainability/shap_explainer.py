import shap
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


def explain_prediction(patient: dict) -> dict:
    """
    Generate SHAP explanation for a single patient prediction.
    Returns feature contributions ranked by importance.
    """
    model       = joblib.load('models/xgb_risk_model.pkl')
    scaler      = joblib.load('models/scaler.pkl')
    feature_cols = joblib.load('models/feature_cols.pkl')

  
    bmi      = patient.get('BMI', 25)
    hba1c    = patient.get('HbA1c', 5.5)
    exercise = patient.get('Exercise_min_day', 30)

    row = {col: patient.get(col, 0) for col in feature_cols
           if col not in ['BMI_Category', 'HbA1c_Zone', 'Exercise_Level']}
    row['BMI_Category']   = 0 if bmi < 18.5 else 1 if bmi < 25 else 2 if bmi < 30 else 3
    row['HbA1c_Zone']     = 0 if hba1c < 5.7 else 1 if hba1c < 6.4 else 2
    row['Exercise_Level'] = 0 if exercise < 10 else 1 if exercise < 30 else 2 if exercise < 60 else 3

    df = pd.DataFrame([row]).reindex(columns=feature_cols, fill_value=0)
    X_scaled = scaler.transform(df)

    explainer  = shap.TreeExplainer(model)
    shap_vals  = explainer.shap_values(X_scaled)

    contributions = {}
    for feat, val in zip(feature_cols, shap_vals[0]):
        contributions[feat] = round(float(val), 4)

    
    sorted_contributions = dict(
        sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
    )

  
    top5 = list(sorted_contributions.items())[:5]

    return {
        'shap_values':         sorted_contributions,
        'top_risk_drivers':    [{'feature': k, 'impact': v} for k, v in top5],
        'explanation_summary': _build_summary(top5, patient)
    }


def _build_summary(top5: list, patient: dict) -> str:
    lines = ["Your risk prediction is driven by:"]
    for feature, impact in top5:
        direction = "increases" if impact > 0 else "decreases"
        val = patient.get(feature, 'N/A')
        lines.append(f"  • {feature} = {val} → {direction} risk (SHAP: {impact:+.3f})")
    return "\n".join(lines)


def plot_shap_bar(patient: dict, save_path: str = 'models/shap_plot.png'):
    """Save a SHAP bar chart for the patient."""
    explanation = explain_prediction(patient)
    shap_dict   = explanation['shap_values']

    features = list(shap_dict.keys())[:10]
    values   = [shap_dict[f] for f in features]
    colors   = ['#e74c3c' if v > 0 else '#2ecc71' for v in values]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(features[::-1], values[::-1], color=colors[::-1])
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel('SHAP Value (Impact on Risk Prediction)')
    ax.set_title('Feature Contributions to Disease Risk')
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    return save_path


if __name__ == '__main__':

    test_patient = {
        'Age': 45, 'Gender': 1, 'BMI': 31, 'Glucose': 155,
        'BloodPressure': 130, 'HbA1c': 8.2, 'Cholesterol': 240,
        'Insulin': 120, 'Exercise_min_day': 10, 'Smoking': 1,
        'Alcohol': 0, 'SleepHours': 5.5, 'MedAdherence': 0.6
    }
    result = explain_prediction(test_patient)
    print(result['explanation_summary'])
    plot_shap_bar(test_patient)
    print("SHAP plot saved.")