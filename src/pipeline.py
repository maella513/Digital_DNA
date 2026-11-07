
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from collect import collect, DEFAULT_SOURCE
from validate import validate_data
from transform import transform_data, save_curated

BASE_DIR = Path(__file__).resolve().parent.parent
REJECTED_DIR = BASE_DIR / "data" / "rejected"
REPORTS_DIR = BASE_DIR / "reports"


def run_pipeline(source_path: Path):
    start = time.perf_counter()

    print("\n=== DIGITAL DNA : PIPELINE ===")

    # 1. Collecte et archivage du fichier brut
    raw_path = collect(source_path)

    # 2. Lecture des données brutes
    df = pd.read_csv(raw_path)
    input_rows = len(df)

    # 3. Validation selon le contrat de données
    accepted, rejected = validate_data(df)

    # 4. Transformation des données acceptées
    curated = transform_data(accepted)
    curated_path = save_curated(curated)

    # 5. Conservation des rejets
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    rejected_path = REJECTED_DIR / "rejected_rows.csv"
    rejected.to_csv(rejected_path, index=False)

    # 6. Rapport d'exécution
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    duplicate_count = int(
        rejected["rejection_reason"]
        .str.contains("Q02_duplicate", na=False)
        .sum()
    )

    duration = round(time.perf_counter() - start, 3)

    report = {
        "pipeline": "digital-dna",
        "executed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_file": raw_path.name,
        "input_rows": input_rows,
        "accepted_rows": len(accepted),
        "rejected_rows": len(rejected),
        "duplicates_removed": duplicate_count,
        "quality_status": (
            "PASS"
            if len(rejected) == 0
            else "PASS_WITH_WARNINGS"
        ),
        "duration_seconds": duration,
        "curated_file": str(
            curated_path.relative_to(BASE_DIR)
        ),
        "rejected_file": str(
            rejected_path.relative_to(BASE_DIR)
        )
    }

    report_path = REPORTS_DIR / "run_report.json"

    report_path.write_text(
        json.dumps(report, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\n=== RÉSULTAT DU PIPELINE ===")
    print(f"Observations entrantes : {input_rows}")
    print(f"Observations acceptées : {len(accepted)}")
    print(f"Observations rejetées : {len(rejected)}")
    print(f"Doublons détectés : {duplicate_count}")
    print(f"Statut : {report['quality_status']}")
    print(f"Durée : {duration} secondes")
    print(f"Dataset curated : {curated_path}")
    print(f"Rapport : {report_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pipeline Digital DNA"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Chemin du fichier CSV source"
    )
    args = parser.parse_args()
    run_pipeline(args.source)
