
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "data" / "digital_dna.db"

TABLE_NAME = "daily_behavior"

DATA_COLUMNS = [
    "user_id",
    "date",
    "screen_time_hours",
    "social_media_hours",
    "sleep_hours",
    "steps",
    "distance_km",
    "notifications",
    "productivity_hours",
    "social_media_ratio",
    "day_of_week",
]


def get_engine(db_path: Path = DB_FILE) -> Engine:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return create_engine(
        f"sqlite:///{db_path.resolve().as_posix()}"
    )


def initialize_database(engine: Engine) -> None:
    """Crée la table et garantit l'unicité utilisateur/date."""

    with engine.begin() as conn:
        conn.execute(
            text("""
                CREATE TABLE IF NOT EXISTS daily_behavior (
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    screen_time_hours REAL NOT NULL,
                    social_media_hours REAL NOT NULL,
                    sleep_hours REAL NOT NULL,
                    steps INTEGER NOT NULL,
                    distance_km REAL NOT NULL,
                    notifications INTEGER NOT NULL,
                    productivity_hours REAL NOT NULL,
                    social_media_ratio REAL,
                    day_of_week TEXT,
                    PRIMARY KEY (user_id, date)
                )
            """)
        )


def load_incremental(
    df: pd.DataFrame,
    db_path: Path = DB_FILE
) -> dict:
    """
    Insère uniquement les observations absentes de SQLite.

    Une observation est identifiée par (user_id, date).
    Les observations déjà présentes sont ignorées.
    """

    missing = set(DATA_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(
            f"Colonnes manquantes pour SQLite : {sorted(missing)}"
        )

    if df[list(DATA_COLUMNS)].isna().any().any():
        raise ValueError(
            "Le dataset contient des valeurs nulles."
        )

    if df.duplicated(["user_id", "date"]).any():
        raise ValueError(
            "Le dataset contient des doublons utilisateur/date."
        )

    records_df = df[DATA_COLUMNS].copy()

    records_df["date"] = pd.to_datetime(
        records_df["date"],
        errors="raise"
    ).dt.strftime("%Y-%m-%d")

    records_df["user_id"] = records_df["user_id"].astype(int)
    records_df["steps"] = records_df["steps"].astype(int)
    records_df["notifications"] = (
        records_df["notifications"].astype(int)
    )

    records = records_df.to_dict(orient="records")

    engine = get_engine(db_path)

    try:
        initialize_database(engine)

        with engine.begin() as conn:
            before = conn.execute(
                text("SELECT COUNT(*) FROM daily_behavior")
            ).scalar_one()

            if records:
                conn.execute(
                    text("""
                        INSERT OR IGNORE INTO daily_behavior (
                            user_id,
                            date,
                            screen_time_hours,
                            social_media_hours,
                            sleep_hours,
                            steps,
                            distance_km,
                            notifications,
                            productivity_hours,
                            social_media_ratio,
                            day_of_week
                        )
                        VALUES (
                            :user_id,
                            :date,
                            :screen_time_hours,
                            :social_media_hours,
                            :sleep_hours,
                            :steps,
                            :distance_km,
                            :notifications,
                            :productivity_hours,
                            :social_media_ratio,
                            :day_of_week
                        )
                    """),
                    records
                )

            after = conn.execute(
                text("SELECT COUNT(*) FROM daily_behavior")
            ).scalar_one()

        return {
            "database_file": str(Path(db_path)),
            "input_rows": len(records),
            "inserted_rows": after - before,
            "already_existing_rows": (
                len(records) - (after - before)
            ),
            "total_rows": after
        }

    finally:
        engine.dispose()


def read_database(db_path: Path = DB_FILE) -> pd.DataFrame:
    """Lit les observations stockées dans SQLite."""

    engine = get_engine(db_path)

    try:
        with engine.connect() as conn:
            return pd.read_sql_query(
                text("""
                    SELECT *
                    FROM daily_behavior
                    ORDER BY user_id, date
                """),
                conn
            )
    finally:
        engine.dispose()
