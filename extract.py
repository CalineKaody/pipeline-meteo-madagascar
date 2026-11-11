"""
ÉTAPE 1 : EXTRACT (extraire)
Ce script va chercher la météo quotidienne de plusieurs villes de Madagascar
sur l'API gratuite Open-Meteo (pas de clé nécessaire) et l'affiche.
Il ne stocke encore rien : on vérifie d'abord que la collecte marche.
"""
import requests
import pandas as pd

# 1) Les villes : nom, latitude, longitude (valeurs approximatives du centre-ville)
VILLES = [
    ("Antananarivo", -18.91, 47.52),
    ("Fianarantsoa", -21.45, 47.09),
    ("Toamasina", -18.15, 49.41),
    ("Mahajanga", -15.72, 46.32),
    ("Toliara", -23.35, 43.67),
    ("Antsiranana", -12.28, 49.29),
    ("Antsirabe", -19.87, 47.03),
    ("Morondava", -20.28, 44.32),
]

URL = "https://api.open-meteo.com/v1/forecast"


def extraire_ville(nom, lat, lon):
    """Interroge l'API pour UNE ville et renvoie un tableau (DataFrame) avec un jour par ligne."""
    parametres = {
        "latitude": lat,
        "longitude": lon,
        # Les mesures quotidiennes demandées :
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Indian/Antananarivo",
        "past_days": 7,        # les 7 derniers jours...
        "forecast_days": 1,    # ...plus aujourd'hui
    }
    reponse = requests.get(URL, params=parametres, timeout=30)
    reponse.raise_for_status()      # s'arrête avec une erreur claire si l'API répond mal
    donnees = reponse.json()        # transforme le texte JSON en dictionnaire Python

    jours = donnees["daily"]        # {"time": [...], "temperature_2m_max": [...], ...}
    tableau = pd.DataFrame(jours)   # un tableau : une colonne par mesure
    tableau.insert(0, "ville", nom) # on ajoute le nom de la ville en première colonne
    return tableau


def main():
    morceaux = []
    for nom, lat, lon in VILLES:
        print(f"Extraction : {nom}...")
        morceaux.append(extraire_ville(nom, lat, lon))

    # On empile les tableaux des 8 villes en un seul
    tout = pd.concat(morceaux, ignore_index=True)
    print()
    print(tout.head(10))
    print(f"\nTotal : {len(tout)} lignes ({tout['ville'].nunique()} villes)")


if __name__ == "__main__":
    main()