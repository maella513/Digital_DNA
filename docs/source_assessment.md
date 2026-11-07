# Digital DNA — Évaluation de la source de données

## 1. Présentation de la source

Digital DNA utilise un jeu de données synthétiques généré localement avec Python, Pandas et NumPy.

Le dataset comprend 15 000 observations correspondant à 500 utilisateurs simulés sur une période de 30 jours.

Chaque observation représente les habitudes quotidiennes d'un utilisateur : temps d'écran, utilisation des réseaux sociaux, sommeil, nombre de pas, distance parcourue, notifications et productivité.

## 2. Origine et méthode de collecte

Les données sont produites par le script `src/generate_data.py`, puis enregistrées dans `data/digital_dna_raw.csv`.

Le collecteur `src/collect.py` archive une copie horodatée dans `data/raw/`, sans modifier le contenu du fichier d'origine.

La génération utilise une graine aléatoire fixe afin de permettre la reproduction du jeu de données.

## 3. Conformité et conditions d'utilisation

Les données sont entièrement synthétiques et ne correspondent pas à des personnes réelles.

Le projet ne collecte aucune donnée personnelle auprès de tiers et ne nécessite ni identifiants, ni clés API, ni accès à un service externe.

Les données sont générées localement pour les besoins pédagogiques du projet.

## 4. Qualité des données

Le pipeline applique six règles de qualité automatisées :

- Q01 : absence de valeurs obligatoires manquantes ;
- Q02 : unicité du couple utilisateur/date ;
- Q03 : respect des plages de valeurs autorisées ;
- Q04 : temps passé sur les réseaux sociaux inférieur ou égal au temps d'écran ;
- Q05 : validité des dates ;
- Q06 : identifiants utilisateurs strictement positifs et entiers.

Les observations invalides sont conservées dans `data/rejected/rejected_rows.csv`, avec leurs motifs de rejet.

## 5. Limites connues

Les comportements sont simulés à partir de distributions et de relations définies dans le générateur.

Ils ne représentent donc pas nécessairement la diversité et la complexité des comportements humains réels.

Les éventuelles relations entre sommeil, temps d'écran, activité physique et productivité sont des hypothèses de simulation, et non des conclusions scientifiques.

Le dataset ne permet pas, à lui seul, de valider des prédictions comportementales sur de véritables utilisateurs.

## 6. Améliorations possibles

Une évolution future consisterait à intégrer des données réelles volontairement fournies par un utilisateur, avec son consentement, afin d'actualiser son jumeau numérique.

Le projet pourrait également intégrer une collecte périodique, un tableau de bord interactif et des modèles prédictifs évalués sur des données appropriées.