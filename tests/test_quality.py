
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from validate import validate_data


def test_quality_rules():
    source = BASE_DIR / "data" / "digital_dna_raw.csv"
    df = pd.read_csv(source).head(2).copy()

    assert len(df) == 2, "Le fichier source doit contenir 2 lignes."

    valid = df.iloc[[0]].copy()
    invalid = []

    # Q01 : valeur manquante
    row = valid.copy()
    row["date"] = "2026-12-01"
    row["sleep_hours"] = None
    invalid.append(row)

    # Q02 : doublon de clé utilisateur/date
    duplicate = valid.copy()
    invalid.append(duplicate)

    # Q03 : durée de sommeil impossible
    row = valid.copy()
    row["date"] = "2026-12-02"
    row["sleep_hours"] = 28
    invalid.append(row)

    # Q04 : réseaux sociaux > temps d'écran
    row = valid.copy()
    row["date"] = "2026-12-03"
    row["screen_time_hours"] = 2
    row["social_media_hours"] = 5
    invalid.append(row)

    # Q05 : date invalide
    row = valid.copy()
    row["date"] = "date_invalide"
    invalid.append(row)

    # Q06 : identifiant utilisateur négatif
    row = valid.copy()
    row["user_id"] = -10
    row["date"] = "2026-12-04"
    invalid.append(row)

    test_data = pd.concat(
        [valid] + invalid,
        ignore_index=True
    )

    accepted, rejected = validate_data(test_data)

    assert len(accepted) == 1
    assert len(rejected) == 6

    reasons = " ".join(rejected["rejection_reason"])

    for rule in ["Q01", "Q02", "Q03", "Q04", "Q05", "Q06"]:
        assert rule in reasons, f"Règle non détectée : {rule}"

    print("6 règles de qualité testées avec succès.")
    print(f"Lignes acceptées : {len(accepted)}")
    print(f"Lignes rejetées : {len(rejected)}")
    print(rejected[["user_id", "date", "rejection_reason"]])


if __name__ == "__main__":
    test_quality_rules()
