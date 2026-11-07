
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT = BASE_DIR / "data/curated/digital_dna_curated.csv"
OUTPUT = BASE_DIR / "data/curated/digital_dna_ml.csv"

df = pd.read_csv(INPUT, parse_dates=["date"])

# Trier les observations chronologiquement
df = df.sort_values(["user_id", "date"]).copy()

# Historique comportemental par utilisateur
group = df.groupby("user_id")

variables = [
    "screen_time_hours",
    "sleep_hours",
    "steps",
    "social_media_hours",
    "notifications",
    "productivity_hours"
]

# Variables du jour précédent
for variable in variables:
    df[f"{variable}_lag0"] = df[variable]
# Moyennes des 3 jours précédents
for variable in [
    "screen_time_hours",
    "sleep_hours",
    "steps"
]:
    df[f"{variable}_rolling3"] = (
        group[variable]
        .transform(lambda s: s.rolling(3).mean())
    )

# Cible : temps d'écran du jour suivant
df["target_screen_time_next_day"] = (
    group["screen_time_hours"].shift(-1)
)

# Jour de la semaine à prédire
df["target_day_of_week"] = (
    (df["date"] + pd.Timedelta(days=1)).dt.day_of_week
)

# Garder les observations avec historique complet
feature_columns = [
    col for col in df.columns
    if col.endswith("_lag0")
    or col.endswith("_rolling3")
]
required = feature_columns + ["target_screen_time_next_day"]

df_ml = df.dropna(subset=required).copy()

df_ml.to_csv(OUTPUT, index=False)

print("Dataset ML créé :", OUTPUT)
print("Observations :", len(df_ml))
print("Variables historiques :", len(feature_columns))
print("Utilisateurs :", df_ml["user_id"].nunique())
