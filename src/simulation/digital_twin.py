import numpy as np
import joblib
import json
import pandas as pd
import tensorflow as tf


class DigitalTwin:
    """
    Core engine. Takes a patient profile, runs risk prediction,
    forecasts future biomarkers, and simulates lifestyle interventions.
    """

    def __init__(self):
        self.risk_model   = joblib.load('models/xgb_risk_model.pkl')
        self.scaler       = joblib.load('models/scaler.pkl')
        self.feature_cols = joblib.load('models/feature_cols.pkl')
        self.lstm_model   = tf.keras.models.load_model('models/lstm_forecaster.h5')

        with open('models/lstm_meta.json') as f:
            meta = json.load(f)
        self.seq_len  = meta['seq_len']
        self.forecast_features = meta['features']


    def predict_risk(self, patient: dict) -> dict:
        """Predict current disease risk for a patient."""
        df = self._to_dataframe(patient)
        scaled = self.scaler.transform(df)
        prob = self.risk_model.predict_proba(scaled)[0][1]
        label = 'High' if prob >= 0.5 else 'Low'
        return {
            'risk_probability': round(float(prob), 4),
            'risk_label':       label,
            'risk_percent':     round(float(prob) * 100, 1)
        }


    def forecast_biomarkers(self, patient: dict, months: int = 12) -> dict:
        """
        Forecast HbA1c, Glucose, BloodPressure for the next `months` months
        based on patient's current values and a simple trend model.
        """
        seed_vals = np.array([[
            patient.get('HbA1c', 7.0),
            patient.get('Glucose', 120),
            patient.get('BloodPressure', 90)
        ]])

       
        sequence = np.repeat(seed_vals, self.seq_len, axis=0)

       
        mean = sequence.mean(axis=0)
        std  = sequence.std(axis=0)
        std[std == 0] = 1
        seq_norm = (sequence - mean) / std

        forecasts = {'HbA1c': [], 'Glucose': [], 'BloodPressure': []}

        for _ in range(months):
            inp = seq_norm[-self.seq_len:].reshape(1, self.seq_len, 3)
            pred_norm = self.lstm_model.predict(inp, verbose=0)[0]
            pred = pred_norm * std + mean  # denormalize

            forecasts['HbA1c'].append(round(float(pred[0]), 2))
            forecasts['Glucose'].append(round(float(pred[1]), 1))
            forecasts['BloodPressure'].append(round(float(pred[2]), 1))

           
            seq_norm = np.vstack([seq_norm, pred_norm])

        forecasts['months'] = list(range(1, months + 1))
        return forecasts


    def simulate_intervention(self, patient: dict, interventions: dict) -> dict:
        """
        Apply lifestyle interventions to patient and re-predict risk.

        interventions example:
        {
            'Exercise_min_day': 45,
            'Smoking': 0,
            'MedAdherence': 0.95,
            'BMI': 26
        }
        """
        original_risk = self.predict_risk(patient)

       
        modified = {**patient, **interventions}
        new_risk  = self.predict_risk(modified)

        
        delta = original_risk['risk_percent'] - new_risk['risk_percent']

        return {
            'original_risk':    original_risk,
            'new_risk':         new_risk,
            'risk_reduction':   round(delta, 1),
            'interventions_applied': interventions,
            'recommendation':   self._generate_recommendation(delta)
        }


    def _generate_recommendation(self, delta: float) -> str:
        if delta >= 20:
            return "Excellent! These changes significantly reduce your risk. Highly recommended."
        elif delta >= 10:
            return "Good impact. These lifestyle changes will meaningfully improve your health."
        elif delta >= 5:
            return "Moderate improvement. Consider combining with additional changes."
        elif delta > 0:
            return "Small improvement. Consult your doctor for a more tailored plan."
        else:
            return "These changes show minimal impact. Please consult a healthcare provider."


    def _to_dataframe(self, patient: dict) -> pd.DataFrame:
        """Convert patient dict to model-ready DataFrame."""
        bmi = patient.get('BMI', 25)
        hba1c = patient.get('HbA1c', 5.5)
        exercise = patient.get('Exercise_min_day', 30)

        row = {col: patient.get(col, 0) for col in self.feature_cols
               if col not in ['BMI_Category', 'HbA1c_Zone', 'Exercise_Level']}

       
        row['BMI_Category'] = (
            0 if bmi < 18.5 else 1 if bmi < 25 else 2 if bmi < 30 else 3
        )
        row['HbA1c_Zone'] = (
            0 if hba1c < 5.7 else 1 if hba1c < 6.4 else 2
        )
        row['Exercise_Level'] = (
            0 if exercise < 10 else 1 if exercise < 30 else 2 if exercise < 60 else 3
        )

        df = pd.DataFrame([row])
       
        df = df.reindex(columns=self.feature_cols, fill_value=0)
        return df