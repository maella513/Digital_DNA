
from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data/curated/digital_dna_ml.csv"
MODEL_PATH = BASE_DIR / "models/screen_time_model.joblib"
OUTPUT_PATH = BASE_DIR / "reports/screen_time_predictions.png"

# Charger le dataset et le modèle
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
features = bundle["features"]

# Reproduire la séparation chronologique du modèle
dates = sorted(df["date"].unique())
cutoff = dates[int(len(dates) * 0.8)]

test = df[df["date"] >= cutoff].copy()

# Prédictions sur les observations de test
test["predicted_screen_time"] = model.predict(test[features])

# Choisir un utilisateur présent dans le test
user_id = 1

user_data = (
    test[test["user_id"] == user_id]
    .sort_values("date")
    .copy()
)

# Les valeurs prédites concernent le lendemain
user_data["prediction_date"] = (
    user_data["date"] + pd.Timedelta(days=1)
)

if user_data.empty:
    raise ValueError(
        f"Aucune observation de test pour l'utilisateur {user_id}"
    )

plt.figure(figsize=(11, 5))

plt.plot(
    user_data["prediction_date"],
    user_data["target_screen_time_next_day"],
    marker="o",
    label="Temps d'écran réel"
)

plt.plot(
    user_data["prediction_date"],
    user_data["predicted_screen_time"],
    marker="s",
    linestyle="--",
    label="Prédiction Random Forest"
)

plt.title(f"Digital DNA — Prédictions utilisateur {user_id}")
plt.xlabel("Date")
plt.ylabel("Temps d'écran (heures)")
plt.legend()
plt.grid(alpha=0.3)
plt.xticks(rotation=30)
plt.tight_layout()

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(OUTPUT_PATH, dpi=180)
plt.show()

print("Graphique enregistré :", OUTPUT_PATH)
