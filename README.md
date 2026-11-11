# Pipeline météo de Madagascar

Pipeline de données de bout en bout : collecte de la météo quotidienne de huit villes de Madagascar via l'API Open-Meteo, nettoyage et contrôle qualité en Python, stockage dans une base **PostgreSQL**, analyses en **SQL** et tableau de bord **Streamlit**.

![Tableau de bord](images/tableau-de-bord.png)

## Architecture

```
API Open-Meteo  ->  extract.py   ->  transform.py   ->  load.py     ->  PostgreSQL  ->  app.py (Streamlit)
(JSON)              extraction       nettoyage et        chargement      base             tableau de bord
                                     contrôles qualité   (upsert)        meteo_madagascar
```

| Étape | Fichier | Rôle |
|---|---|---|
| Extract | `extract.py` | Interroge l'API pour 8 villes (7 jours passés + aujourd'hui) |
| Transform | `transform.py` | Renomme les colonnes, convertit les types, contrôle la qualité, ajoute `temp_moy` et `jour_pluvieux` |
| Load | `load.py` | Crée les tables, insère les villes et les mesures (sans doublons) |
| Analyse | `db/analyses.sql` | Cinq requêtes d'analyse (agrégations, `DISTINCT ON`, fonction de fenêtre `RANK`) |
| Restitution | `app.py` | Tableau de bord Streamlit avec filtre par ville |

## Villes

Antananarivo, Fianarantsoa, Toamasina, Mahajanga, Toliara, Antsiranana, Antsirabe, Morondava (coordonnées approximatives du centre-ville).

## Base de données

Deux tables (`db/schema.sql`) :

- `villes` : `id`, `nom` (unique), `latitude`, `longitude`
- `meteo_quotidienne` : `ville_id` (clé étrangère vers `villes`), `date`, `temp_max`, `temp_min`, `pluie_mm`, `temp_moy`, `jour_pluvieux`

La clé primaire `(ville_id, date)` garantit une seule ligne par ville et par jour. Des contraintes `CHECK` refusent les données absurdes (`temp_min > temp_max`, pluie négative).

## Choix techniques

- **Idempotence** : le chargement utilise `INSERT ... ON CONFLICT DO UPDATE`. Relancer le pipeline ne crée pas de doublons.
- **Qualité des données** : le script affiche les anomalies détectées (valeurs manquantes, doublons, valeurs improbables) avant de nettoyer.
- **Pluie manquante = 0 mm** : choix de modélisation, à revoir si l'API change de comportement.
- **Secrets** : les identifiants de la base sont lus dans un fichier `.env`, exclu de Git par `.gitignore`.

## Installation

Prérequis : Python 3.10 ou plus, PostgreSQL.

```bash
# 1. Environnement virtuel (Windows : venv\Scripts\activate ; Linux/macOS : source venv/bin/activate)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Créer une base vide nommée meteo_madagascar (pgAdmin ou : createdb meteo_madagascar)

# 3. Copier .env.example en .env puis renseigner DB_PASSWORD
```

## Utilisation

```bash
python load.py          # lance tout le pipeline : extraction, nettoyage, chargement
streamlit run app.py    # ouvre le tableau de bord sur http://localhost:8501
```

Les requêtes d'analyse de `db/analyses.sql` peuvent être exécutées dans pgAdmin ou avec `psql`.

## Captures d'écran

| Graphiques par ville | Données |
|---|---|
| ![Graphiques](images/graphiques.png) | ![Données](images/donnees.png) |

## Limites et pistes d'amélioration

- La fenêtre de données est courte (8 jours). Pour une vraie analyse, utiliser l'API d'archive d'Open-Meteo pour remonter plusieurs années.
- Le pipeline se lance à la main. Il pourrait être planifié chaque jour (planificateur de tâches Windows, cron ou Airflow).
- Pas encore de tests automatisés ni de conteneur Docker (une base PostgreSQL et le pipeline lançables avec `docker compose`).
- Les coordonnées des villes sont approximatives.

## Auteure

Câline Fetison – étudiante en Master SIGD (EMIT) et en Master Objets connectés et cybersécurité (ENI), Madagascar.
