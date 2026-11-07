
from pathlib import Path
import argparse

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data/curated/digital_dna_curated.csv"
MODEL_PATH = BASE_DIR / "models/screen_time_model.joblib"


def predict_user(user_id):
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]

    df = pd.read_csv(DATA_PATH, parse_dates=["date"])

    user_data = (
        df[df["user_id"] == user_id]
        .sort_values("date")
        .copy()
    )

    if len(user_data) < 3:
        raise ValueError(
            "Au moins 3 jours d'historique sont nécessaires."
        )

    latest = user_data.iloc[-1]
    prediction_date = latest["date"] + pd.Timedelta(days=1)

    variables = [
        "screen_time_hours",
        "sleep_hours",
        "steps",
        "social_media_hours",
        "notifications",
        "productivity_hours"
    ]

    row = {}

    # Dernières valeurs observées au jour J
    for variable in variables:
        row[f"{variable}_lag0"] = float(latest[variable])

    # Moyennes des jours J-2, J-1 et J
    for variable in [
        "screen_time_hours",
        "sleep_hours",
        "steps"
    ]:
        row[f"{variable}_rolling3"] = float(
            user_data[variable].tail(3).mean()
        )

    row["target_day_of_week"] = prediction_date.day_of_week

    X = pd.DataFrame([row])[features]
    prediction = float(model.predict(X)[0])

    print("\n=== DIGITAL DNA — PREDICTION PERSONNALISEE ===")
    print("Utilisateur :", user_id)
    print("Derniere observation :", latest["date"].date())
    print("Date predite :", prediction_date.date())
    print("Temps d'ecran estime :", round(prediction, 2), "h")

    print(
        "Dernier temps d'ecran observe :",
        round(row["screen_time_hours_lag0"], 2),
        "h"
    )

    print(
        "Moyenne des 3 derniers jours :",
        round(row["screen_time_hours_rolling3"], 2),
        "h"
    )

    return prediction


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=int, default=1)
    args = parser.parse_args()

    predict_user(args.user)
