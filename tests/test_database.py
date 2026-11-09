
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from database import load_incremental, read_database


def sample_data():
    return pd.DataFrame([
        {
            "user_id": 1,
            "date": "2026-10-01",
            "screen_time_hours": 5.0,
            "social_media_hours": 2.0,
            "sleep_hours": 8.0,
            "steps": 7000,
            "distance_km": 5.0,
            "notifications": 80,
            "productivity_hours": 6.0,
            "social_media_ratio": 0.4,
            "day_of_week": "Thursday",
        }
    ])


def test_initial_insert(tmp_path):
    db = tmp_path / "test.db"

    result = load_incremental(sample_data(), db)

    assert result["inserted_rows"] == 1
    assert result["total_rows"] == 1


def test_no_duplicate_on_second_run(tmp_path):
    db = tmp_path / "test.db"
    df = sample_data()

    load_incremental(df, db)
    result = load_incremental(df, db)

    assert result["inserted_rows"] == 0
    assert result["already_existing_rows"] == 1
    assert result["total_rows"] == 1


def test_incremental_new_observation(tmp_path):
    db = tmp_path / "test.db"

    df = sample_data()
    load_incremental(df, db)

    new_df = df.copy()
    new_df["date"] = "2026-10-02"

    result = load_incremental(new_df, db)

    assert result["inserted_rows"] == 1
    assert result["total_rows"] == 2


def test_database_read(tmp_path):
    db = tmp_path / "test.db"

    load_incremental(sample_data(), db)
    stored = read_database(db)

    assert len(stored) == 1
    assert stored.iloc[0]["user_id"] == 1
