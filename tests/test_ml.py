
from pathlib import Path

import joblib
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data/curated/digital_dna_curated.csv"
MODEL_PATH = BASE_DIR / "models/screen_time_model.joblib"
CLUSTERS_PATH = BASE_DIR / "data/curated/user_clusters.csv"
PCA_PATH = BASE_DIR / "data/curated/clusters_pca.csv"


@pytest.fixture(scope="module")
def data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])


@pytest.fixture(scope="module")
def model_bundle():
    return joblib.load(MODEL_PATH)


def build_test_features(user_data, features):
    """Reproduit les variables utilisées pour la prédiction."""
    user_data = user_data.sort_values("date")
    latest = user_data.iloc[-1]
    next_date = latest["date"] + pd.Timedelta(days=1)

    row = {}

    variables = [
        "screen_time_hours",
        "sleep_hours",
        "steps",
        "social_media_hours",
        "notifications",
        "productivity_hours"
    ]

    for variable in variables:
        row[f"{variable}_lag0"] = float(latest[variable])

    for variable in [
        "screen_time_hours",
        "sleep_hours",
        "steps"
    ]:
        row[f"{variable}_rolling3"] = float(
            user_data[variable].tail(3).mean()
        )

    row["target_day_of_week"] = next_date.day_of_week

    return pd.DataFrame([row])[features]


def test_dataset_not_empty(data):
    assert not data.empty


def test_users_count(data):
    assert data["user_id"].nunique() == 500


def test_no_duplicate_user_dates(data):
    assert not data.duplicated(
        subset=["user_id", "date"]
    ).any()


def test_model_features(model_bundle):
    features = model_bundle["features"]

    assert len(features) == 10
    assert len(features) == len(set(features))
    assert "screen_time_hours_lag0" in features
    assert "target_day_of_week" in features


@pytest.mark.parametrize("user_id", [1, 25, 150, 400])
def test_user_prediction(data, model_bundle, user_id):
    user_data = data[data["user_id"] == user_id]

    assert len(user_data) >= 3

    X = build_test_features(
        user_data,
        model_bundle["features"]
    )

    prediction = model_bundle["model"].predict(X)[0]

    assert pd.notna(prediction)
    assert 0 <= prediction <= 24


def test_simulation_does_not_modify_original(data):
    user_data = (
        data[data["user_id"] == 1]
        .sort_values("date")
        .copy()
    )

    original = user_data.copy(deep=True)
    simulated = user_data.copy(deep=True)

    last_index = simulated.index[-1]

    simulated.loc[
        last_index, "screen_time_hours"
    ] = 5.0

    pd.testing.assert_frame_equal(user_data, original)


def test_clusters_cover_all_users(data):
    clusters = pd.read_csv(CLUSTERS_PATH)

    assert clusters["user_id"].is_unique
    assert set(clusters["user_id"]) == set(data["user_id"])


def test_pca_coordinates():
    pca = pd.read_csv(PCA_PATH)

    assert len(pca) == 500
    assert pca[["PCA_1", "PCA_2"]].notna().all().all()
