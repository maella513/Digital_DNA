
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "digital_dna.db"

METRICS = [
    "screen_time_hours",
    "social_media_hours",
    "sleep_hours",
    "steps",
    "distance_km",
    "notifications",
    "productivity_hours"
]


class DigitalTwin:

    def __init__(self, user_id):
        self.user_id = int(user_id)
        self.history = self.load_history()

    def load_history(self):
        """Récupère l'historique individuel."""

        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(
                """
                SELECT *
                FROM daily_behavior
                WHERE user_id = ?
                ORDER BY date
                """,
                conn,
                params=(self.user_id,)
            )

        if df.empty:
            raise ValueError(
                f"Aucune donnée pour l'utilisateur {self.user_id}"
            )

        df["date"] = pd.to_datetime(df["date"])
        return df

    def get_profile(self):
        """Construit le profil comportemental."""

        averages = self.history[METRICS].mean()

        profile = {
            "user_id": self.user_id,
            "observations": len(self.history),
            "last_update": str(
                self.history["date"].max().date()
            ),
            "averages": averages.round(2).to_dict()
        }

        return profile

    def get_evolution(self, window=7):
        """Compare deux périodes successives."""

        df = self.history.sort_values("date")

        if len(df) < window * 2:
            return {}

        previous = df.iloc[-2 * window:-window]
        recent = df.iloc[-window:]

        evolution = {}

        for metric in METRICS:
            old = previous[metric].mean()
            new = recent[metric].mean()

            change = (
                (new - old) / old * 100
                if old != 0 else None
            )

            evolution[metric] = {
                "previous": round(float(old), 2),
                "recent": round(float(new), 2),
                "change_percent": (
                    round(float(change), 2)
                    if change is not None else None
                )
            }

        return evolution

    def refresh(self):
        """Actualise le jumeau depuis SQLite."""

        self.history = self.load_history()
        return self.get_profile()

    def summary(self):
        """Affiche un résumé du jumeau."""

        profile = self.get_profile()

        print("\n=== DIGITAL DNA : PERSONAL DIGITAL TWIN ===")
        print(f"Utilisateur : {self.user_id}")
        print(f"Observations : {profile['observations']}")
        print(f"Dernière observation : {profile['last_update']}")

        print("\nPROFIL COMPORTEMENTAL")
        for metric, value in profile["averages"].items():
            print(f"{metric}: {value}")

        print("\nÉVOLUTION SUR 7 JOURS")
        evolution = self.get_evolution()

        for metric, values in evolution.items():
            print(
                f"{metric}: "
                f"{values['previous']} -> "
                f"{values['recent']} "
                f"({values['change_percent']}%)"
            )


if __name__ == "__main__":

    twin = DigitalTwin(user_id=25)
    twin.summary()
