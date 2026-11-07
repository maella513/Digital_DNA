
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)

N_USERS = 500
N_DAYS = 30

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Profils individuels persistants
users = pd.DataFrame({
    "user_id": np.arange(1, N_USERS + 1),
    "base_screen": rng.uniform(2, 9, N_USERS),
    "base_sleep": rng.uniform(5.5, 9, N_USERS),
    "base_steps": rng.uniform(2000, 13000, N_USERS),
    "base_social_ratio": rng.uniform(0.2, 0.7, N_USERS),
    "screen_trend": rng.normal(0, 0.025, N_USERS)
})

# Historique de 30 jours
dates = pd.date_range("2026-10-01", periods=N_DAYS)

df = pd.MultiIndex.from_product(
    [users["user_id"], dates],
    names=["user_id", "date"]
).to_frame(index=False)

df = df.merge(users, on="user_id", how="left")

df["day_index"] = (df["date"] - dates[0]).dt.days

n = len(df)

# Comportements évolutifs
df["screen_time_hours"] = np.clip(
    df["base_screen"]
    + df["screen_trend"] * df["day_index"]
    + rng.normal(0, 0.7, n),
    0.5, 14
).round(2)

df["social_media_hours"] = (
    df["screen_time_hours"]
    * df["base_social_ratio"]
).round(2)

df["sleep_hours"] = np.clip(
    df["base_sleep"]
    - 0.08 * (df["screen_time_hours"] - df["base_screen"])
    + rng.normal(0, 0.4, n),
    3, 11
).round(2)

df["steps"] = np.clip(
    df["base_steps"]
    + rng.normal(0, 1200, n),
    0, 25000
).astype(int)

df["distance_km"] = (
    df["steps"] * 0.00075
).round(2)

df["notifications"] = np.clip(
    df["screen_time_hours"] * rng.uniform(12, 35, n),
    0, 500
).astype(int)

df["productivity_hours"] = np.clip(
    8 - 0.35 * df["screen_time_hours"]
    + rng.normal(0, 0.7, n),
    0, 8
).round(2)

# Données observables finales
columns = [
    "user_id", "date",
    "screen_time_hours",
    "social_media_hours",
    "sleep_hours",
    "steps",
    "distance_km",
    "notifications",
    "productivity_hours"
]

df = df[columns]

# Export
output = DATA_DIR / "digital_dna_raw.csv"
df.to_csv(output, index=False)

print("DIGITAL DNA - DATASET GENERATED")
print(f"Observations : {len(df)}")
print(f"Users : {df['user_id'].nunique()}")
print(f"Days : {N_DAYS}")
print(f"File : {output}")

print("\nSample:")
print(df.head())
