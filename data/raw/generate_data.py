import pandas as pd
import numpy as np

np.random.seed(42)
n = 1000

df = pd.DataFrame({
    'Age':               np.random.randint(25, 75, n),
    'Gender':            np.random.choice([0, 1], n),           # 0=F, 1=M
    'BMI':               np.round(np.random.normal(28, 6, n), 1),
    'Glucose':           np.random.randint(70, 200, n),
    'BloodPressure':     np.random.randint(60, 140, n),
    'HbA1c':             np.round(np.random.uniform(4.5, 12.0, n), 1),
    'Cholesterol':       np.random.randint(150, 300, n),
    'Insulin':           np.random.randint(15, 300, n),
    'Exercise_min_day':  np.random.randint(0, 90, n),
    'Smoking':           np.random.choice([0, 1], n, p=[0.7, 0.3]),
    'Alcohol':           np.random.choice([0, 1], n, p=[0.6, 0.4]),
    'SleepHours':        np.round(np.random.normal(6.5, 1.5, n), 1),
    'MedAdherence':      np.round(np.random.uniform(0.3, 1.0, n), 2),
})


risk_score = (
    (df['HbA1c'] > 7.5).astype(int) * 2 +
    (df['BMI'] > 30).astype(int) +
    (df['Glucose'] > 140).astype(int) +
    (df['BloodPressure'] > 130).astype(int) +
    (df['Smoking'] == 1).astype(int) +
    (df['Exercise_min_day'] < 20).astype(int) +
    (df['MedAdherence'] < 0.6).astype(int)
)
df['DiseaseRisk'] = (risk_score >= 4).astype(int)

df.to_csv('data/raw/patients.csv', index=False)
print(f"Dataset saved: {df.shape}")
print(df['DiseaseRisk'].value_counts())