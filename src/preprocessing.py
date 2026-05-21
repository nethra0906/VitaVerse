import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

def load_and_clean(path='data/raw/patients.csv'):
    df = pd.read_csv(path)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    for col in ['BMI', 'Glucose', 'Cholesterol', 'Insulin']:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        df[col] = df[col].clip(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)

    df['BMI_Category'] = pd.cut(df['BMI'],
        bins=[0, 18.5, 24.9, 29.9, 100],
        labels=[0, 1, 2, 3]).astype(int)

    df['HbA1c_Zone'] = pd.cut(df['HbA1c'],
        bins=[0, 5.7, 6.4, 100],
        labels=[0, 1, 2]).astype(int)

    df['Exercise_Level'] = pd.cut(df['Exercise_min_day'],
        bins=[-1, 10, 30, 60, 200],
        labels=[0, 1, 2, 3]).astype(int)

    return df


def split_and_scale(df, target='DiseaseRisk', test_size=0.2):
    feature_cols = [c for c in df.columns if c != target]
    X = df[feature_cols]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

  
    os.makedirs('models', exist_ok=True)
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(feature_cols, 'models/feature_cols.pkl')

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_cols


if __name__ == '__main__':
    df = load_and_clean()
    df.to_csv('data/processed/patients_clean.csv', index=False)
    print("Cleaned data saved.")
    print(df.head())
    print(df.dtypes)