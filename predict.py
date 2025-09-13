import os
import joblib
import pandas as pd

# ==========================
# 1. CONFIG
# ==========================
DATA_PATH = "data\processed\cleaned_weather.csv"   # <-- change if needed
MODEL_DIR = "app\models"
LAG_HOURS = 24  # use the same lag length as training

# ==========================
# 2. HELPER FUNCTIONS
# ==========================
def load_models(model_dir):
    """Load all trained models from directory into a dict"""
    models = {}
    for fname in os.listdir(model_dir):
        if fname.endswith(".joblib"):
            key = fname.replace(".joblib", "")
            models[key] = joblib.load(os.path.join(model_dir, fname))
    print(f"✅ Loaded {len(models)} models from {model_dir}")
    return models


def create_lagged_features(df, variables, lags):
    """Create lagged features efficiently without fragmentation warnings."""
    lagged_data = {}
    for var in variables:
        for lag in lags:
            lagged_data[f"{var}_lag{lag}"] = df[var].shift(lag).values
    df_lagged = pd.DataFrame(lagged_data, index=df.index)
    return pd.concat([df, df_lagged], axis=1)


# ==========================
# 3. MAIN FORECASTING PIPELINE
# ==========================
def main():
    print("📂 Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    # Drop non-numeric / categorical cols like "time"
    if "time" in df.columns:
        df = df.drop(columns=["time"])

    # Convert all to numeric (in case some are objects)
    df = df.apply(pd.to_numeric, errors="coerce")

    # Create lagged features
    variables = df.columns.tolist()
    df_lagged = create_lagged_features(df, variables, lags=range(1, LAG_HOURS + 1))

    # Drop NaNs introduced by lagging
    df_lagged = df_lagged.dropna()

    print("📂 Loading models...")
    models = load_models(MODEL_DIR)

    print("🔮 Forecasting next steps...\n")
    print("=== Forecast Results ===")

    # Take the latest row as input
    last_row = df_lagged.iloc[[-1]]

    for name, model in models.items():
        try:
            # Align features with training set
            if hasattr(model, "get_booster"):
                model_features = model.get_booster().feature_names
                input_aligned = last_row.reindex(columns=model_features, fill_value=0)
            else:
                input_aligned = last_row

            y_pred = model.predict(input_aligned)[0]
            print(f"{name}: {y_pred:.3f}")
        except Exception as e:
            print(f"{name}: Error: {e}")


# ==========================
# 4. RUN
# ==========================
if __name__ == "__main__":
    main()

