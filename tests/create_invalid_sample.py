
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

source = BASE_DIR / "data" / "digital_dna_raw.csv"
output = BASE_DIR / "tests" / "sample_with_errors.csv"

# Charger 100 observations originales
df = pd.read_csv(source).head(100).copy()

# Introduire 4 erreurs sur des lignes différentes

# Q01 : valeur manquante
df.loc[0, "sleep_hours"] = None

# Q03 : sommeil impossible
df.loc[1, "sleep_hours"] = 28

# Q04 : réseaux sociaux > temps d'écran
df.loc[2, "screen_time_hours"] = 2
df.loc[2, "social_media_hours"] = 8

# Q05 : date invalide
df.loc[3, "date"] = "date_invalide"

# Ajouter un doublon de la ligne 4
df = pd.concat(
    [df, df.iloc[[4]]],
    ignore_index=True
)

df.to_csv(output, index=False)

print(f"Fichier créé : {output}")
print(f"Observations : {len(df)}")
