"""
ÉTAPE 2 : TRANSFORM (transformer)
On réutilise l'extraction (extract.py), puis on nettoie et on contrôle les données.
Le résultat est enregistré dans data/meteo_propre.csv.
"""
import os
import pandas as pd
from extract import VILLES, extraire_ville   # on réutilise le code de l'étape 1


def extraire_tout():
    """Extrait les 8 villes et empile les tableaux en un seul."""
    morceaux = [extraire_ville(nom, lat, lon) for nom, lat, lon in VILLES]
    return pd.concat(morceaux, ignore_index=True)


def transformer(brut):
    """Nettoie le tableau brut et renvoie un tableau propre."""
    df = brut.copy()

    # 1) Noms de colonnes plus clairs
    df = df.rename(columns={
        "time": "date",
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
        "precipitation_sum": "pluie_mm",
    })

    # 2) Types : la date devient une vraie date, les mesures des nombres
    df["date"] = pd.to_datetime(df["date"]).dt.date
    for colonne in ["temp_max", "temp_min", "pluie_mm"]:
        df[colonne] = pd.to_numeric(df[colonne], errors="coerce")  # texte illisible -> vide

    # 3) Contrôles de qualité : on affiche les problèmes au lieu de les cacher
    manquantes = df[["temp_max", "temp_min", "pluie_mm"]].isna().sum().sum()
    doublons = df.duplicated(subset=["ville", "date"]).sum()
    incoherentes = (df["temp_min"] > df["temp_max"]).sum()
    hors_plage = ((df["temp_max"] > 50) | (df["temp_min"] < -5)).sum()
    pluie_negative = (df["pluie_mm"] < 0).sum()
    print("--- Contrôle qualité ---")
    print(f"Valeurs manquantes        : {manquantes}")
    print(f"Doublons (ville + date)   : {doublons}")
    print(f"Température min > max     : {incoherentes}")
    print(f"Températures improbables  : {hors_plage}")
    print(f"Pluie négative            : {pluie_negative}")

    # 4) Nettoyage : on retire les doublons et les lignes sans mesure
    df = df.drop_duplicates(subset=["ville", "date"])
    df = df.dropna(subset=["temp_max", "temp_min"])
    df = df[df["temp_min"] <= df["temp_max"]]
    df["pluie_mm"] = df["pluie_mm"].fillna(0)   # pas de valeur de pluie = 0 mm (choix à documenter)

    # 5) Colonnes calculées
    df["temp_moy"] = ((df["temp_max"] + df["temp_min"]) / 2).round(1)
    df["jour_pluvieux"] = df["pluie_mm"] >= 1

    return df.reset_index(drop=True)


def main():
    brut = extraire_tout()
    propre = transformer(brut)

    os.makedirs("data", exist_ok=True)
    propre.to_csv("data/meteo_propre.csv", index=False)

    print()
    print(propre.head(10).to_string())
    print(f"\n{len(brut)} lignes brutes -> {len(propre)} lignes propres")
    print("Fichier écrit : data/meteo_propre.csv")


if __name__ == "__main__":
    main()