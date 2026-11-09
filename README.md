# Digital DNA — Jumeau numérique comportemental

**Projet Data Engineering, Machine Learning & Intelligence Artificielle**

**ESEO — Cycle ingénieur, spécialité IA & Data | 2026-2027**

## 1. Présentation

Digital DNA est un projet de collecte, de traitement et d'analyse de données visant à construire un **jumeau numérique comportemental** à partir d'observations quotidiennes.

Le système permet de reconstituer les habitudes numériques d'un utilisateur, d'analyser leur évolution, d'identifier différents profils comportementaux et de prédire certaines habitudes futures grâce au Machine Learning.

Une application web interactive développée avec **Streamlit** permet d'explorer les données, de visualiser les profils utilisateurs et de simuler différents comportements.

**Problématique :** Comment collecter, fiabiliser, stocker et exploiter des données d'habitudes quotidiennes afin de construire un profil numérique individuel évolutif et prédictif ?

Le projet a été réalisé dans le cadre du module **Architectures BD et collecte de données — ESEO**.

## 2. Objectifs

- Construire une chaîne de collecte et de traitement reproductible.
- Automatiser la validation et la transformation des données.
- Détecter les anomalies et conserver les observations rejetées.
- Centraliser les observations validées dans une base relationnelle SQLite.
- Mettre en place une ingestion incrémentale sans duplication.
- Produire des rapports de qualité et d'exécution.
- Identifier des profils comportementaux grâce au clustering.
- Prédire le temps d'écran du lendemain avec un modèle de Machine Learning.
- Développer une interface interactive de visualisation et de simulation.
- Automatiser les tests avec Pytest et GitHub Actions.

## 3. Données utilisées

Le projet utilise un dataset entièrement synthétique de **15 000 observations**, représentant **500 utilisateurs suivis pendant 30 jours**.

| Variable | Description |
|---|---|
| `user_id` | Identifiant de l'utilisateur |
| `date` | Date de l'observation |
| `screen_time_hours` | Temps d'écran quotidien (heures) |
| `social_media_hours` | Temps consacré aux réseaux sociaux (heures) |
| `sleep_hours` | Durée du sommeil (heures) |
| `steps` | Nombre de pas quotidiens |
| `distance_km` | Distance parcourue (kilomètres) |
| `notifications` | Nombre de notifications |
| `productivity_hours` | Temps de productivité simulé (heures) |

Deux variables supplémentaires sont calculées lors de la transformation :

- `social_media_ratio` : proportion du temps d'écran consacrée aux réseaux sociaux.
- `day_of_week` : jour de la semaine.

**Important :** les données sont entièrement synthétiques et ne correspondent pas à des personnes réelles. Les analyses et prédictions illustrent une démarche technique et ne constituent pas des conclusions scientifiques sur les comportements humains.

## 4. Architecture de données

Digital DNA repose sur une architecture modulaire associant **ETL, stockage relationnel, Machine Learning et visualisation interactive**.

### Pipeline ETL

Le pipeline principal, `src/pipeline.py`, comprend les étapes suivantes :

1. **Génération :** création de données synthétiques avec Python et NumPy.
2. **Collecte :** lecture et archivage horodaté des données brutes.
3. **Validation :** application des règles définies dans le contrat YAML.
4. **Transformation :** nettoyage, typage et enrichissement des observations acceptées.
5. **Stockage :** export CSV et chargement incrémental dans SQLite.
6. **Reporting :** génération d'un rapport JSON contenant les indicateurs d'exécution.

### Organisation des flux

```text
Données synthétiques (CSV)
          |
          v
Collecte et archivage
          |
          v
Validation des données
          |
          v
Transformation et enrichissement
          |
          +--------------------------+
          |                          |
          v                          v
Dataset CSV curated          Base SQLite
          |                  daily_behavior
          |                          |
          v                          |
Machine Learning                    |
Clustering / Prédiction             |
          |                          |
          +--------------------------+
          |
          v
Application Streamlit

Contrôles qualité -> Rejets CSV
                  -> Rapport JSON

Tests Pytest -> GitHub Actions (CI)
```

Le diagramme d'architecture initial est disponible dans `docs/architecture.png`. Il peut être actualisé pour représenter les nouveaux composants.

## 5. Stockage relationnel SQLite

Le pipeline intègre désormais un stockage relationnel persistant avec **SQLite et SQLAlchemy**.

Les observations validées sont chargées dans la table `daily_behavior`.

### Structure de la table

La table contient les données comportementales et les indicateurs dérivés.

Une clé primaire composée garantit l'unicité de chaque observation :

`PRIMARY KEY (user_id, date)`

### Ingestion incrémentale

Le module `src/database.py` assure le chargement incrémental des observations.

Il permet :

- D'insérer uniquement les nouvelles observations.
- D'ignorer les couples utilisateur/date déjà présents.
- De conserver les données historiques.
- De relancer le pipeline sans créer de doublons.
- De consulter les données stockées en base.

Les dates sont normalisées au format `YYYY-MM-DD`.

L'insertion utilise une stratégie `INSERT OR IGNORE`, associée à une contrainte d'unicité.

**Remarque :** les observations existantes ne sont pas mises à jour automatiquement si leurs valeurs changent. Le mécanisme actuel privilégie l'ajout de nouvelles observations.

## 6. Contrat et qualité des données

Le contrat de données est défini dans :

`config/data_contract.yaml`

Six règles principales sont appliquées :

| Règle | Contrôle |
|---|---|
| Q01 | Absence de valeurs obligatoires manquantes |
| Q02 | Unicité du couple utilisateur/date |
| Q03 | Respect des plages numériques autorisées |
| Q04 | Temps sur les réseaux sociaux inférieur ou égal au temps d'écran |
| Q05 | Validité des dates |
| Q06 | Identifiants utilisateurs strictement positifs et entiers |

Les observations non conformes sont conservées dans :

`data/rejected/rejected_rows.csv`

Le rapport d'exécution est enregistré dans :

`reports/run_report.json`

Il contient notamment le nombre de lignes entrantes, acceptées et rejetées, le statut qualité, la durée du traitement et les statistiques de chargement SQLite.

## 7. Machine Learning — Prédiction du temps d'écran

Digital DNA intègre un modèle supervisé permettant d'estimer le **temps d'écran d'un utilisateur à J+1**.

### Préparation des données

Les observations sont transformées en variables explicatives temporelles :

- Valeurs récentes des indicateurs comportementaux.
- Variables retardées (*lags*).
- Moyennes mobiles sur trois jours.
- Informations temporelles.

Le dataset final utilisé pour l'entraînement et l'évaluation contient **13 500 observations**.

### Modèles évalués

Deux approches ont été comparées :

- Un modèle de référence (*baseline*).
- Un modèle **Random Forest Regressor**, développé avec Scikit-learn.

### Résultats

| Indicateur | Baseline | Random Forest |
|---|---:|---:|
| MAE | 0,8014 | **0,6588** |
| RMSE | 1,0064 | **0,8313** |
| R² | 0,7969 | **0,8615** |

Le modèle Random Forest obtient une réduction d'environ **17,8 % de l'erreur absolue moyenne** par rapport à la baseline.

Ces résultats sont obtenus sur les données synthétiques du projet.

## 8. Clustering et profils comportementaux

Une approche non supervisée basée sur **K-Means** permet de regrouper les utilisateurs selon leurs habitudes numériques.

Le nombre de clusters a été choisi à partir d'une comparaison des scores de silhouette.

**Configuration retenue : 2 clusters, avec un score de silhouette de 0,3700.**

| Profil | Utilisateurs | Caractéristiques |
|---|---:|---|
| Modéré | 239 | Temps d'écran et usage des réseaux sociaux plus faibles |
| Intensif | 261 | Temps d'écran et notifications plus élevés |

Une analyse en composantes principales (**PCA**) permet de représenter les utilisateurs dans un espace bidimensionnel.

Les deux premières composantes expliquent environ **76,97 % de la variance**.

Ces profils sont descriptifs et dépendent des données synthétiques générées.

## 9. Application interactive Streamlit

L'application web permet d'explorer le jumeau numérique à travers cinq espaces fonctionnels :

1. **Vue d'ensemble :** indicateurs globaux et statistiques du dataset.
2. **Profil utilisateur :** consultation des habitudes d'un utilisateur sélectionné.
3. **Prédictions ML :** estimation du temps d'écran du lendemain.
4. **Simulateur :** exploration de scénarios comportementaux.
5. **Clustering et PCA :** visualisation des groupes d'utilisateurs et de leur positionnement.

L'interface utilise **Streamlit et Plotly** pour présenter des indicateurs, graphiques et visualisations interactives.

## 10. Technologies utilisées

| Domaine | Technologies |
|---|---|
| Développement | Python 3.13 |
| Traitement de données | Pandas, NumPy |
| Validation | PyYAML, contrat de données |
| Base de données | SQLite, SQLAlchemy |
| Machine Learning | Scikit-learn, Joblib |
| Visualisation | Plotly, Matplotlib |
| Application web | Streamlit |
| Tests | Pytest |
| Intégration continue | GitHub Actions |
| Versionnement | Git, GitHub |

## 11. Installation

### Prérequis

- Python 3.13 recommandé.
- Git, pour cloner le dépôt.
- Un terminal PowerShell ou équivalent.

### Cloner le projet

```bash
git clone https://github.com/maella513/Digital_DNA.git
cd Digital_DNA
```

### Créer un environnement virtuel

```bash
python -m venv .venv
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

### Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

## 12. Exécution du projet

### Générer les données synthétiques

```bash
python src/generate_data.py
```

### Exécuter le pipeline ETL complet

```bash
python src/pipeline.py
```

Le pipeline produit ou actualise :

- `data/raw/` : archives horodatées des données brutes.
- `data/curated/digital_dna_curated.csv` : observations validées.
- `data/rejected/rejected_rows.csv` : observations rejetées.
- `data/digital_dna.db` : base relationnelle SQLite.
- `reports/run_report.json` : rapport d'exécution.

### Lancer l'application Streamlit

```bash
python -m streamlit run app.py
```

L'application est généralement accessible à l'adresse :

`http://localhost:8501`

### Exécuter les tests

```bash
python -m pytest tests/ -v
```

### Démontrer la gestion des rejets

```bash
python tests/create_invalid_sample.py
python src/pipeline.py --source tests/sample_with_errors.csv
```

Le jeu d'essai prévu contient 101 observations, dont 96 acceptées et 5 rejetées.

Pour restaurer le dataset CSV principal :

```bash
python src/pipeline.py
```

**Attention :** le chargement SQLite est incrémental. Restaurer le CSV principal ne supprime pas les observations déjà insérées en base.

## 13. Tests et intégration continue

Le projet dispose d'une suite de **16 tests Pytest réussis**.

| Domaine | Nombre de tests |
|---|---:|
| SQLite et ingestion incrémentale | 4 |
| Machine Learning et clustering | 11 |
| Qualité des données | 1 |
| **Total** | **16** |

Les tests vérifient notamment :

- La validité du dataset.
- L'absence de doublons.
- La cohérence des variables ML.
- Le fonctionnement des prédictions.
- La couverture des utilisateurs par les clusters.
- La présence des coordonnées PCA.
- L'insertion initiale en base.
- L'idempotence des chargements SQLite.
- L'ajout de nouvelles observations.
- La lecture des données stockées.

### GitHub Actions

Un workflow GitHub Actions automatise les tests lors des modifications envoyées sur la branche principale et des pull requests ciblant cette branche.

Le workflow prépare l'environnement Python, installe les dépendances et exécute Pytest.

**État vérifié : tests réussis localement et workflow GitHub Actions validé.**

Cette automatisation correspond à une démarche d'intégration continue (**CI**). Le déploiement automatique n'est pas encore intégré.

## 14. Idempotence et reproductibilité

Le pipeline peut être exécuté plusieurs fois sur le même jeu de données.

- Le fichier CSV curated est régénéré à chaque exécution.
- Les rejets et le rapport JSON sont actualisés.
- La base SQLite conserve les observations existantes.
- Les nouvelles observations sont insérées uniquement si leur clé utilisateur/date est absente.

Cette architecture distingue donc les fichiers de sortie du lot courant du stockage historique en base relationnelle.

## 15. Limites connues

- Les données sont synthétiques et ne reflètent pas nécessairement des comportements réels.
- La collecte reste locale et réalisée par lots CSV.
- L'ingestion SQLite est incrémentale, mais ne gère pas encore les mises à jour des observations existantes.
- Les fichiers CSV curated et rejected sont remplacés à chaque exécution.
- Les modèles ML ont été évalués sur les données synthétiques du projet.
- Le déploiement automatisé et la supervision de production ne sont pas encore intégrés.
- L'application Streamlit fonctionne localement ; son accessibilité publique dépend d'un déploiement distinct.

## 16. Perspectives d'amélioration

- Connecter des sources de données externes via API.
- Mettre en place une collecte planifiée ou en streaming.
- Ajouter une stratégie d'upsert pour actualiser les observations existantes.
- Étendre l'architecture vers PostgreSQL ou un environnement cloud.
- Améliorer la robustesse et la généralisation des modèles prédictifs.
- Ajouter des contrôles de qualité et des tests d'intégration supplémentaires.
- Mettre en place un déploiement continu et une supervision applicative.
- Renforcer la confidentialité et la sécurité pour une éventuelle utilisation de données réelles.

## 17. Documentation

| Fichier | Description |
|---|---|
| `docs/architecture.png` | Diagramme d'architecture initial |
| `docs/source_assessment.md` | Description et limites de la source |
| `config/data_contract.yaml` | Contrat de données |
| `src/pipeline.py` | Pipeline ETL principal |
| `src/database.py` | Stockage SQLite et ingestion incrémentale |
| `src/etl_pipeline.py` | Prototype ETL SQLite initial |
| `reports/run_report.json` | Rapport de la dernière exécution |
| `tests/test_database.py` | Tests du stockage SQLite |
| `tests/test_ml.py` | Tests des fonctionnalités ML |
| `tests/test_quality.py` | Tests de qualité des données |
| `.github/workflows/tests.yml` | Workflow d'intégration continue |

---

**Digital DNA — ESEO 2026-2027**

Projet académique associant Data Engineering, architecture de bases de données, Machine Learning et visualisation interactive.