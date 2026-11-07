
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

# Configuration des chemins
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RAW_FILE = DATA_DIR / "digital_dna_raw.csv"
DB_FILE = DATA_DIR / "digital_dna.db"

REQUIRED_COLUMNS = [
    "user_id", "date",
    "screen_time_hours",
    "social_media_hours",
    "sleep_hours",
    "steps",
    "distance_km",
    "notifications",
    "productivity_hours"
]

def extract():
    print("1. EXTRACTION")
    df = pd.read_csv(RAW_FILE)
    print(f"Observations extraites : {len(df)}")
    return df


def transform(df):
    print("\n2. TRANSFORMATION")
    df = df.copy()

    # Vérifier les colonnes
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {missing}")

    # Conversion des types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_cols = [
        col for col in REQUIRED_COLUMNS
        if col not in ["user_id", "date"]
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["user_id"] = pd.to_numeric(
        df["user_id"], errors="coerce"
    )

    # Nettoyage des valeurs manquantes
    before = len(df)
    df = df.dropna(subset=REQUIRED_COLUMNS)
    print(f"Lignes incomplètes supprimées : {before - len(df)}")

    # Suppression des doublons utilisateur/date
    before = len(df)
    df = df.drop_duplicates(
        subset=["user_id", "date"],
        keep="last"
    )
    print(f"Doublons supprimés : {before - len(df)}")

    # Validation des contraintes métier
    valid = (
        (df["user_id"] > 0)
        & (df["user_id"] % 1 == 0)
        & df["screen_time_hours"].between(0, 24)
        & df["social_media_hours"].between(0, 24)
        & (df["social_media_hours"] <= df["screen_time_hours"])
        & df["sleep_hours"].between(0, 24)
        & df["productivity_hours"].between(0, 24)
        & df["steps"].between(0, 100000)
        & df["distance_km"].between(0, 100)
        & df["notifications"].between(0, 10000)
    )

    rejected = (~valid).sum()
    df = df.loc[valid].copy()

    print(f"Lignes invalides supprimées : {rejected}")

    # Typage et tri
    df["user_id"] = df["user_id"].astype(int)
    df = df.sort_values(["user_id", "date"])

    # Indicateurs dérivés
    df["social_media_ratio"] = (
        df["social_media_hours"]
        / df["screen_time_hours"].replace(0, float("nan"))
    ).fillna(0).round(3)

    df["day_of_week"] = df["date"].dt.day_name()

    print(f"Observations validées : {len(df)}")
    return df


def load(df):
    print("\n3. CHARGEMENT SQLITE")

    engine = create_engine(f"sqlite:///{DB_FILE.as_posix()}")

    # Création ou remplacement de la table
    df.to_sql(
        "daily_behavior",
        con=engine,
        if_exists="replace",
        index=False
    )

    # Vérification SQL
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM daily_behavior")
        )
        count = result.scalar()

    print(f"Observations stockées : {count}")
    print(f"Base de données : {DB_FILE}")

    engine.dispose()


def main():
    print("=== DIGITAL DNA : ETL PIPELINE ===")

    df = extract()
    df_clean = transform(df)

    if df_clean.empty:
        raise ValueError("Aucune donnée valide à charger.")

    load(df_clean)

    print("\nETL TERMINÉ AVEC SUCCÈS !")


if __name__ == "__main__":
    main()
