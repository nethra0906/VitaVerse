import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from xgboost import XGBClassifier
import sys
sys.path.append('.')
from src.preprocessing import load_and_clean, split_and_scale


def train_risk_model():
   
    df = load_and_clean('data/raw/patients.csv')
    X_train, X_test, y_train, y_test, scaler, feature_cols = split_and_scale(df)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=50
    )

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\n── Classification Report ──────────────────────")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/xgb_risk_model.pkl')
    print("\nModel saved to models/xgb_risk_model.pkl")

    return model


if __name__ == '__main__':
    train_risk_model()