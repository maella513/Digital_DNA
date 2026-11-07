
from pathlib import Path
import pandas as pd
import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACT_PATH = BASE_DIR / "config" / "data_contract.yaml"
REJECTED_DIR = BASE_DIR / "data" / "rejected"


def validate_data(df: pd.DataFrame):
    """Valide les données selon le contrat YAML."""

    with open(CONTRACT_PATH, encoding="utf-8") as file:
        contract = yaml.safe_load(file)

    columns = contract["columns"]
    required = [
        name for name, spec in columns.items()
        if spec.get("required", False)
    ]

    missing_columns = [
        name for name in required
        if name not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {missing_columns}"
        )

    data = df.copy()
    reasons = pd.Series(
        "",
        index=data.index,
        dtype="string"
    )

    def reject(mask, reason):
        nonlocal reasons
        mask = mask.fillna(False)
        reasons.loc[mask] = (
            reasons.loc[mask] + reason + "; "
        )

    # Q01 : valeurs obligatoires
    reject(
        data[required].isna().any(axis=1)
        | data[required].astype("string")
            .apply(lambda col: col.str.strip().eq(""))
            .any(axis=1),
        "Q01_missing_value"
    )

    # Conversion et validation des types
    for name, spec in columns.items():
        expected_type = spec["type"]

        if expected_type == "date":
            data[name] = pd.to_datetime(
                data[name],
                errors="coerce",
                format="%Y-%m-%d"
            )

            reject(
                data[name].isna(),
                "Q05_invalid_date"
            )

        elif expected_type in ("integer", "float"):
            numeric = pd.to_numeric(
                data[name],
                errors="coerce"
            )

            invalid_type = numeric.isna() & (
                df[name].notna()
            )

            if expected_type == "integer":
                invalid_type = invalid_type | (
                    numeric.notna()
                    & (numeric % 1 != 0)
                )

            reject(
                invalid_type,
                f"invalid_type_{name}"
            )

            data[name] = numeric

            if "min" in spec:
                reject(
                    numeric < spec["min"],
                    f"Q03_below_min_{name}"
                )

            if "max" in spec:
                reject(
                    numeric > spec["max"],
                    f"Q03_above_max_{name}"
                )

    # Q06 : identifiants utilisateurs positifs
    reject(
        data["user_id"].isna()
        | (data["user_id"] <= 0)
        | (data["user_id"] % 1 != 0),
        "Q06_invalid_user_id"
    )

    # Q04 : réseaux sociaux <= temps d'écran
    reject(
        data["social_media_hours"]
        > data["screen_time_hours"],
        "Q04_social_exceeds_screen"
    )

    # Q02 : doublons utilisateur/date
    # On conserve la première occurrence.
    duplicates = data.duplicated(
        subset=contract["primary_key"],
        keep="first"
    )

    reject(
        duplicates,
        "Q02_duplicate"
    )

    accepted = data.loc[reasons.eq("")].copy()

    rejected = df.loc[reasons.ne("")].copy()
    rejected["rejection_reason"] = (
        reasons.loc[reasons.ne("")].str.rstrip("; ")
    )

    # Format cohérent pour les données acceptées
    for name, spec in columns.items():
        if spec["type"] == "integer":
            accepted[name] = accepted[name].astype(int)

        elif spec["type"] == "date":
            accepted[name] = (
                accepted[name].dt.strftime("%Y-%m-%d")
            )

    return accepted, rejected


if __name__ == "__main__":

    raw_files = sorted(
        (BASE_DIR / "data" / "raw").glob("*.csv")
    )

    if not raw_files:
        raise FileNotFoundError(
            "Aucun fichier dans data/raw/"
        )

    source = max(
        raw_files,
        key=lambda path: path.stat().st_mtime_ns
    )

    print(f"Validation de : {source.name}")

    df = pd.read_csv(source)

    accepted, rejected = validate_data(df)

    REJECTED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    rejected.to_csv(
        REJECTED_DIR / "rejected_rows.csv",
        index=False
    )

    print(f"Lignes entrantes : {len(df)}")
    print(f"Lignes acceptées : {len(accepted)}")
    print(f"Lignes rejetées : {len(rejected)}")
    print("Fichier de rejets enregistré.")
