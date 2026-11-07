
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUTPUT = Path(__file__).resolve().parent / "architecture.png"

fig, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 12)
ax.set_ylim(0, 11)
ax.axis("off")

def node(x, y, w, h, title, subtitle, color="#EAF2F8"):
    rect = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.12",
        facecolor=color,
        edgecolor="#274C77",
        linewidth=1.4
    )
    ax.add_patch(rect)
    ax.text(
        x + w / 2, y + h * 0.63,
        title, ha="center", va="center",
        fontsize=10, fontweight="bold"
    )
    ax.text(
        x + w / 2, y + h * 0.28,
        subtitle, ha="center", va="center",
        fontsize=8
    )

def arrow(x1, y1, x2, y2):
    ax.add_patch(
        FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.5,
            color="#526777"
        )
    )

ax.text(
    6, 10.55,
    "DIGITAL DNA — Architecture de collecte et traitement",
    ha="center", fontsize=15, fontweight="bold"
)

node(3.5, 9.2, 5, 0.8,
     "Generation synthetique",
     "generate_data.py | 500 utilisateurs x 30 jours")

node(3.5, 7.9, 5, 0.8,
     "Collecte RAW",
     "collect.py | copie CSV horodatee")

node(3.5, 6.6, 5, 0.8,
     "Validation",
     "validate.py | contrat YAML | 6 regles")

node(0.7, 5.1, 4.7, 0.8,
     "CURATED",
     "transform.py | donnees validees", "#E4F4E8")

node(6.6, 5.1, 4.7, 0.8,
     "REJECTED",
     "CSV | observations et motifs", "#FBE8E6")

node(3.5, 3.7, 5, 0.8,
     "Rapport d'execution",
     "run_report.json | volumes et qualite")

node(0.7, 1.8, 4.7, 0.8,
     "SQLite",
     "etl_pipeline.py | chargement distinct")

node(6.6, 1.8, 4.7, 0.8,
     "Digital Twin",
     "digital_twin.py | profil et evolution")

arrow(6, 9.2, 6, 8.7)
arrow(6, 7.9, 6, 7.4)
arrow(6, 6.6, 3.05, 5.9)
arrow(6, 6.6, 8.95, 5.9)
arrow(3.05, 5.1, 5.4, 4.5)
arrow(8.95, 5.1, 6.6, 4.5)

# Flux SQLite indépendant du pipeline curated
arrow(3.05, 1.8, 8.95, 1.8)

ax.text(
    6, 3.0,
    "Le stockage SQLite est actuellement alimente separement.",
    ha="center", fontsize=9, style="italic"
)

plt.savefig(
    OUTPUT,
    dpi=180,
    bbox_inches="tight",
    facecolor="white"
)

plt.close()
print(f"Diagramme genere : {OUTPUT}")
