import pandas as pd
import numpy as np
import os
import joblib
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import re

# Parameters
LAG_HOURS = 24
FORECAST_HOURS = 6
TARGET_VARS = [
    "wind_speed_100m (km/h)",
    "wind_direction_100m (°)",
    "pressure_msl (hPa)",
    "vapour_pressure_deficit (kPa)",
    "soil_moisture_100_to_255cm (m³/m³)"
]

def sanitize_filename(name: str) -> str:
    """Remove illegal filename chars (Windows safe)."""
    return re.sub(r'\W+', '_', name)

def create_lag_features(df: pd.DataFrame, target_vars: list, lag_hours: int) -> pd.DataFrame:
    """Efficient lag creation using concat instead of repeated insert."""
    lagged_frames = [df]
    for var in target_vars:
        if var not in df.columns:
            print(f"⚠️ Skipping missing feature {var}")
            continue
        lagged = pd.concat(
            {f"{var}_lag{lag}": df[var].shift(lag) for lag in range(1, lag_hours + 1)},
            axis=1
        )
        lagged_frames.append(lagged)
    return pd.concat(lagged_frames, axis=1)

def create_forecast_targets(df: pd.DataFrame, target_vars: list, forecast_hours: int) -> pd.DataFrame:
    df_targets = df.copy()
    for var in target_vars:
        if var not in df.columns:
            print(f"⚠️ Skipping missing target {var}")
            continue
        for step in range(1, forecast_hours + 1):
            df_targets[f"{var}_t+{step}"] = df[var].shift(-step)
    return df_targets

def train_xgboost_models(X_train, y_train, X_test, y_test, target_columns, model_dir="app/models"):
    os.makedirs(model_dir, exist_ok=True)
    models = {}
    for target in target_columns:
        print(f"🚀 Training model for {target}...")
        model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        model.fit(X_train, y_train[target])
        
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test[target], preds))
        print(f"✅ RMSE for {target}: {rmse:.3f}")
        
        # Sanitize file name
        safe_name = sanitize_filename(target)
        model_file = os.path.join(model_dir, f"xgb_{safe_name}.joblib")
        
        joblib.dump(model, model_file)
        models[target] = model
    return models

if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_weather.csv")
    df_lagged = create_lag_features(df, TARGET_VARS, LAG_HOURS)
    df_full = create_forecast_targets(df_lagged, TARGET_VARS, FORECAST_HOURS)
    df_full = df_full.dropna()

    feature_cols = [col for col in df_full.columns if "lag" in col]
    target_cols = [col for col in df_full.columns if "_t+" in col]

    X = df_full[feature_cols]
    y = df_full[target_cols]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    models = train_xgboost_models(X_train, y_train, X_test, y_test, target_cols)

    print("🎉 Training complete. Models saved in app/models/")
