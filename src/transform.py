
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
CURATED_DIR = BASE_DIR / "data" / "curated"


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transforme les observations validées."""

    data = df.copy()

    # Normaliser les dates
    data["date"] = pd.to_datetime(data["date"])

    # Part du temps d'écran consacrée aux réseaux sociaux
    data["social_media_ratio"] = (
        data["social_media_hours"]
        / data["screen_time_hours"].replace(0, float("nan"))
    ).fillna(0).round(4)

    # Jour de la semaine : lundi = 0
    data["day_of_week"] = data["date"].dt.dayofweek

    # Trier les observations
    data = data.sort_values(
        ["user_id", "date"]
    ).reset_index(drop=True)

    # Format de date standard
    data["date"] = data["date"].dt.strftime("%Y-%m-%d")

    return data


def save_curated(df: pd.DataFrame) -> Path:
    """Enregistre le dataset nettoyé."""

    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = CURATED_DIR / "digital_dna_curated.csv"

    df.to_csv(output_path, index=False)

    return output_path


if __name__ == "__main__":

    from validate import validate_data

    raw_dir = BASE_DIR / "data" / "raw"
    raw_files = list(raw_dir.glob("*.csv"))

    if not raw_files:
        raise FileNotFoundError(
            "Aucun fichier brut trouvé dans data/raw/"
        )

    source = max(
        raw_files,
        key=lambda path: path.stat().st_mtime_ns
    )

    raw_data = pd.read_csv(source)

    accepted, rejected = validate_data(raw_data)

    curated = transform_data(accepted)
    output = save_curated(curated)

    print("\n=== DIGITAL DNA : TRANSFORMATION ===")
    print(f"Fichier source : {source.name}")
    print(f"Observations initiales : {len(raw_data)}")
    print(f"Observations validées : {len(accepted)}")
    print(f"Observations rejetées : {len(rejected)}")
    print(f"Colonnes finales : {len(curated.columns)}")
    print(f"Dataset curated : {output}")
