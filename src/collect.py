
from pathlib import Path
from datetime import datetime, timezone
import argparse
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

DEFAULT_SOURCE = BASE_DIR / "data" / "digital_dna_raw.csv"


def collect(source_path: Path) -> Path:
    """Archive une copie brute horodatée du fichier source."""

    source_path = source_path.expanduser().resolve()

    if not source_path.is_file():
        raise FileNotFoundError(
            f"Source introuvable : {source_path}"
        )

    if source_path.stat().st_size == 0:
        raise ValueError("Le fichier source est vide.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S_%fZ"
    )

    destination = RAW_DIR / f"digital_dna_{timestamp}.csv"

    # Copie des octets sans transformation
    shutil.copyfile(source_path, destination)

    print("Collecte terminée.")
    print(f"Source : {source_path}")
    print(f"Fichier raw : {destination.name}")
    print(f"Taille : {destination.stat().st_size} octets")

    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Collecteur Digital DNA"
    )

    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Chemin du CSV à collecter"
    )

    args = parser.parse_args()

    try:
        collect(args.source)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Erreur de collecte : {error}\n")
