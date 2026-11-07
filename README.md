# Digital DNA — Jumeau numérique comportemental

## Présentation

Digital DNA est un projet de collecte et de traitement de données visant à construire un jumeau numérique comportemental à partir d'observations quotidiennes.

L'application permet de reconstituer les habitudes d'un utilisateur, de suivre leur évolution et de préparer leur exploitation dans un système d'analyse personnalisé.

**Question centrale :** Comment collecter, fiabiliser et exploiter des données d'habitudes quotidiennes pour construire un profil numérique individuel évolutif ?

Ce projet a été développé dans le cadre du module **Architectures BD et collecte de données — ESEO, 2026-2027**.

## Objectifs

- Construire une chaîne de collecte reproductible.
- Valider les données selon un contrat défini.
- Détecter les anomalies et conserver les observations rejetées.
- Produire un dataset fiable et exploitable.
- Générer un rapport d'exécution.
- Analyser les habitudes individuelles à travers un jumeau numérique.

## Données utilisées

Le projet utilise un dataset synthétique de **15 000 observations**, représentant **500 utilisateurs sur 30 jours**.

Chaque observation contient les informations suivantes :

| Variable | Description |
|---|---|
| `user_id` | Identifiant de l'utilisateur |
| `date` | Date de l'observation |
| `screen_time_hours` | Temps d'écran quotidien, en heures |
| `social_media_hours` | Temps consacré aux réseaux sociaux, en heures |
| `sleep_hours` | Durée du sommeil, en heures |
| `steps` | Nombre de pas quotidiens |
| `distance_km` | Distance parcourue, en kilomètres |
| `notifications` | Nombre de notifications |
| `productivity_hours` | Temps de productivité simulé, en heures |

Deux variables sont ajoutées après transformation : `social_media_ratio` et `day_of_week`.

Les données sont entièrement synthétiques et ne représentent pas des personnes réelles.

## Cas d'usage

1. Consulter le profil comportemental d'un utilisateur.
2. Comparer ses habitudes entre différentes périodes.
3. Actualiser son profil à partir de nouvelles observations.

## Indicateurs principaux

- Temps d'écran quotidien moyen.
- Durée moyenne de sommeil.
- Nombre moyen de pas quotidiens.

## Architecture

Le pipeline comprend les étapes suivantes :

1. **Génération :** création des données synthétiques avec Python et NumPy.
2. **Collecte :** archivage horodaté du fichier brut.
3. **Validation :** application des règles du contrat de données.
4. **Transformation :** enrichissement des observations acceptées.
5. **Stockage :** export des données validées et des rejets.
6. **Reporting :** production d'un rapport JSON.

Le diagramme complet se trouve dans `docs/architecture.png`.

Le projet comprend également un prototype de jumeau numérique utilisant SQLite. Son chargement est actuellement réalisé séparément par `src/etl_pipeline.py`.

## Technologies

- Python 3.11+
- Pandas et NumPy
- PyYAML
- SQLite et SQLAlchemy
- Matplotlib
- Scikit-learn, Plotly et Streamlit pour les extensions analytiques prévues

## Installation

Cloner le dépôt GitHub ou récupérer l'archive ZIP du projet.

Créer un environnement virtuel :

```powershell
python -m venv .venv
```

Activer l'environnement sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```powershell
python -m pip install -r requirements.txt
```

## Exécution

### 1. Générer les données synthétiques

```powershell
python src/generate_data.py
```

### 2. Exécuter le pipeline complet

```powershell
python src/pipeline.py
```

Le pipeline produit :

- Une copie brute horodatée dans `data/raw/`.
- Le dataset nettoyé dans `data/curated/digital_dna_curated.csv`.
- Les observations rejetées dans `data/rejected/rejected_rows.csv`.
- Un rapport dans `reports/run_report.json`.

### 3. Exécuter les tests de qualité

```powershell
python tests/test_quality.py
```

### 4. Démontrer les rejets

```powershell
python tests/create_invalid_sample.py
python src/pipeline.py --source tests/sample_with_errors.csv
```

Cette démonstration doit produire 101 observations entrantes, 96 acceptées et 5 rejetées.

### 5. Restaurer le dataset principal

```powershell
python src/pipeline.py
```

### 6. Utiliser le prototype de jumeau numérique

```powershell
python src/etl_pipeline.py
python src/digital_twin.py
```

## Contrat et règles de qualité

Le contrat est défini dans `config/data_contract.yaml`.

Six règles sont appliquées :

- **Q01 :** valeurs obligatoires non manquantes.
- **Q02 :** unicité du couple `user_id` et `date`.
- **Q03 :** valeurs numériques dans les plages autorisées.
- **Q04 :** temps sur les réseaux sociaux inférieur ou égal au temps d'écran.
- **Q05 :** dates valides.
- **Q06 :** identifiants utilisateurs strictement positifs et entiers.

Les observations rejetées sont conservées avec leur motif.

## Idempotence

Le pipeline reconstruit le dataset `curated` à chaque exécution.

Une seconde exécution avec la même source ne crée donc pas de doublons supplémentaires.

Le fichier de sortie contient 15 000 observations et aucun doublon sur le couple `user_id` / `date` lorsque la source principale est utilisée.

## Limites connues

- Les données sont synthétiques et ne permettent pas de conclure sur des comportements humains réels.
- La collecte est actuellement locale et réalisée par lots.
- Le pipeline principal ne met pas encore automatiquement à jour SQLite.
- Les fichiers de sortie `curated`, `rejected` et le rapport sont remplacés à chaque exécution.
- Les fonctionnalités prédictives et le tableau de bord interactif restent à développer.

## Améliorations futures

- Intégrer de nouvelles observations sans reconstruire l'ensemble de l'historique.
- Connecter automatiquement le pipeline validé à SQLite.
- Ajouter un tableau de bord Streamlit.
- Développer des prévisions comportementales et des simulations interactives.
- Évaluer les modèles prédictifs sur des données adaptées.

## Documentation

- `docs/architecture.png` : diagramme d'architecture.
- `docs/source_assessment.md` : description, conformité et limites de la source.
- `config/data_contract.yaml` : contrat de données.
- `reports/run_report.json` : rapport de la dernière exécution.