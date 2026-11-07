
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data/curated/digital_dna_ml.csv"
MODEL_PATH = BASE_DIR / "models/screen_time_model.joblib"
REPORT_PATH = BASE_DIR / "reports/ml_metrics.json"

# 1. Charger les données
df = pd.read_csv(DATA_PATH, parse_dates=["date"])

df = df.sort_values(["date", "user_id"])

# 2. Sélectionner les variables explicatives
features = [
    col for col in df.columns
    if col.endswith("_lag0") or col.endswith("_rolling3")
]

features.append("target_day_of_week")
assert len(features) == len(set(features)), (
    f"Variables dupliquées : {features}"
)

target = "target_screen_time_next_day"

# 3. Séparation chronologique
dates = sorted(df["date"].unique())

split_index = int(len(dates) * 0.8)
cutoff_date = dates[split_index]

train = df[df["date"] < cutoff_date]
test = df[df["date"] >= cutoff_date]

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

# 4. Baseline : dernière valeur observée
# Les variables _lag1 décrivent la veille de la date courante.
baseline_predictions = test["screen_time_hours_lag0"].to_numpy()
# 5. Entraîner le modèle
model = RandomForestRegressor(
    n_estimators=150,
    max_depth=12,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# 6. Prédictions
predictions = model.predict(X_test)

# 7. Évaluation
def evaluate(y_true, y_pred):
    return {
        "MAE": round(
            float(mean_absolute_error(y_true, y_pred)), 4
        ),
        "RMSE": round(
            float(np.sqrt(mean_squared_error(y_true, y_pred))), 4
        ),
        "R2": round(
            float(r2_score(y_true, y_pred)), 4
        )
    }

baseline_metrics = evaluate(
    y_test, baseline_predictions
)

model_metrics = evaluate(
    y_test, predictions
)

# 8. Sauvegarder le modèle
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(
    {"model": model, "features": features},
    MODEL_PATH
)

# 9. Rapport d'évaluation
report = {
    "target": target,
    "model": "RandomForestRegressor",
    "split": "chronological_80_20",
    "train_rows": len(train),
    "test_rows": len(test),
    "train_end_date": str(train["date"].max().date()),
    "test_start_date": str(test["date"].min().date()),
    "baseline": baseline_metrics,
    "random_forest": model_metrics,
    "feature_importance": {
        name: round(float(importance), 4)
        for name, importance in sorted(
            zip(features, model.feature_importances_),
            key=lambda x: x[1],
            reverse=True
        )
    }
}

REPORT_PATH.write_text(
    json.dumps(report, indent=4, ensure_ascii=False),
    encoding="utf-8"
)

print("\n=== DIGITAL DNA — EVALUATION ML ===")
print("Entrainement :", len(train), "observations")
print("Test :", len(test), "observations")

print("\nBaseline :", baseline_metrics)
print("Random Forest :", model_metrics)

print("\nVariables les plus importantes :")
for name, importance in list(
    report["feature_importance"].items()
)[:5]:
    print(f"  {name}: {importance:.4f}")

print("\nModele sauvegarde :", MODEL_PATH)
print("Rapport sauvegarde :", REPORT_PATH)
