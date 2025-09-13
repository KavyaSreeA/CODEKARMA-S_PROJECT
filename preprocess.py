import pandas as pd
import os

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load the raw CSV file and return a pandas DataFrame.
    """
    # Read the CSV file, skip first 3 rows (metadata)
    df = pd.read_csv(file_path, skiprows=3)

    # Convert "time" column to datetime format
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset:
    1. Convert numeric columns
    2. Handle missing values
    """
    # Convert all columns except "time" to numeric
    for col in df.columns:
        if col != "time":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle missing values: fill with forward fill, then backward fill
    df = df.fillna(method="ffill").fillna(method="bfill")

    return df


def save_dataset(df: pd.DataFrame, output_path: str):
    """
    Save the cleaned DataFrame to a CSV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    # File paths
    raw_file = "data/raw/open-meteo-13.11N80.25E15m.csv"
    cleaned_file = "data/processed/cleaned_weather.csv"

    # Load raw dataset
    print("Loading dataset...")
    df = load_dataset(raw_file)

    # Clean dataset
    print("Cleaning dataset...")
    df_clean = clean_dataset(df)

    # Save cleaned dataset
    print("Saving cleaned dataset...")
    save_dataset(df_clean, cleaned_file)

    print("✅ Dataset cleaned and saved at:", cleaned_file)
