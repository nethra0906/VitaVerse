import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib, os, json


def generate_time_series_data(n_patients=200, n_months=24):
    """Simulate monthly biomarker readings per patient."""
    records = []
    np.random.seed(42)

    for pid in range(n_patients):
        base_hba1c = np.random.uniform(5.5, 10.0)
        base_glucose = np.random.uniform(90, 180)
        base_bp = np.random.uniform(70, 140)

        for t in range(n_months):
            records.append({
                'patient_id': pid,
                'month':      t,
                'HbA1c':      round(base_hba1c + 0.05 * t + np.random.normal(0, 0.2), 2),
                'Glucose':    round(base_glucose + 0.8 * t + np.random.normal(0, 5), 1),
                'BloodPressure': round(base_bp + 0.3 * t + np.random.normal(0, 3), 1),
            })

    df = pd.DataFrame(records)
    os.makedirs('data/simulated', exist_ok=True)
    df.to_csv('data/simulated/timeseries.csv', index=False)
    return df


def create_sequences(data, seq_len=6):
    """Convert time series into (X, y) sequences."""
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i + seq_len])
        y.append(data[i + seq_len])
    return np.array(X), np.array(y)


def train_lstm():
    df = generate_time_series_data()

    features = ['HbA1c', 'Glucose', 'BloodPressure']
    SEQ_LEN  = 6  

    all_X, all_y = [], []

    for pid in df['patient_id'].unique():
        patient_df = df[df['patient_id'] == pid].sort_values('month')
        values = patient_df[features].values

        
        mean, std = values.mean(axis=0), values.std(axis=0)
        std[std == 0] = 1
        values_norm = (values - mean) / std

        X, y = create_sequences(values_norm, SEQ_LEN)
        all_X.append(X)
        all_y.append(y)

    X_all = np.concatenate(all_X)
    y_all = np.concatenate(all_y)

 
    split = int(0.8 * len(X_all))
    X_train, X_test = X_all[:split], X_all[split:]
    y_train, y_test = y_all[:split], y_all[split:]

   
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(SEQ_LEN, len(features))),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(len(features))
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.summary()

    es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[es],
        verbose=1
    )

    loss, mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest Loss: {loss:.4f} | MAE: {mae:.4f}")
  
    model.save('models/lstm_forecaster.h5')
    meta = {'seq_len': SEQ_LEN, 'features': features}
    with open('models/lstm_meta.json', 'w') as f:
        json.dump(meta, f)

    print("LSTM model saved.")
    return model


if __name__ == '__main__':
    train_lstm()