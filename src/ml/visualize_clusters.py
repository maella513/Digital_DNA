
from pathlib import Path

import joblib
import pandas as pd
from sklearn.decomposition import PCA

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = BASE_DIR / "data/curated/user_clusters.csv"
MODEL_PATH = BASE_DIR / "models/clustering_model.joblib"
OUTPUT_PATH = BASE_DIR / "data/curated/clusters_pca.csv"

profiles = pd.read_csv(INPUT_PATH)
bundle = joblib.load(MODEL_PATH)

scaler = bundle["scaler"]
features = bundle["features"]

# Utiliser la normalisation du clustering
X_scaled = scaler.transform(profiles[features])

# Réduire les six dimensions à deux
pca = PCA(n_components=2)
coordinates = pca.fit_transform(X_scaled)

profiles["PCA_1"] = coordinates[:, 0]
profiles["PCA_2"] = coordinates[:, 1]

profiles.to_csv(OUTPUT_PATH, index=False)

print("\n=== DIGITAL DNA — PCA ===")
print("Utilisateurs :", len(profiles))
print(
    "Variance expliquée :",
    round(pca.explained_variance_ratio_.sum() * 100, 2),
    "%"
)
print("Fichier enregistré :", OUTPUT_PATH)
