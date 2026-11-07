
from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "data/curated/digital_dna_curated.csv"
OUTPUT_PATH = BASE_DIR / "data/curated/user_clusters.csv"
MODEL_PATH = BASE_DIR / "models/clustering_model.joblib"

df = pd.read_csv(DATA_PATH)

variables = [
    "screen_time_hours",
    "social_media_hours",
    "sleep_hours",
    "steps",
    "notifications",
    "productivity_hours"
]

# Construire un profil moyen par utilisateur
profiles = (
    df.groupby("user_id")[variables]
    .mean()
    .reset_index()
)

# Normalisation des variables
scaler = StandardScaler()
X = scaler.fit_transform(profiles[variables])

# Tester plusieurs nombres de groupes
scores = {}

for k in range(2, 7):
    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(X)
    scores[k] = silhouette_score(X, labels)

best_k = max(scores, key=scores.get)

# Entraîner le modèle final
model = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10
)

profiles["cluster"] = model.fit_predict(X)

# Enregistrer les résultats
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

profiles.to_csv(OUTPUT_PATH, index=False)

joblib.dump(
    {
        "model": model,
        "scaler": scaler,
        "features": variables
    },
    MODEL_PATH
)

print("\n=== DIGITAL DNA — CLUSTERING ===")
print("Scores silhouette :", scores)
print("Nombre optimal de groupes :", best_k)

print("\nRépartition des utilisateurs :")
print(profiles["cluster"].value_counts().sort_index())

print("\nCaractéristiques moyennes par groupe :")
print(
    profiles.groupby("cluster")[variables]
    .mean()
    .round(2)
)

print("\nRésultats enregistrés :", OUTPUT_PATH)
