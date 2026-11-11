"""
ÉTAPE 3 : LOAD (charger)
Lance tout le pipeline : extraire -> transformer -> charger dans PostgreSQL.
Les identifiants de connexion sont lus dans le fichier .env (jamais écrits dans le code).
"""
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from extract import VILLES
from transform import extraire_tout, transformer

load_dotenv()   # lit le fichier .env et met son contenu dans les variables d'environnement


def connecter():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "meteo_madagascar"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def creer_tables(curseur):
    """Exécute db/schema.sql (sans danger si les tables existent déjà)."""
    with open("db/schema.sql", encoding="utf-8") as f:
        curseur.execute(f.read())


def charger_villes(curseur):
    """Insère les villes et renvoie un dictionnaire {nom: id}."""
    execute_values(
        curseur,
        """INSERT INTO villes (nom, latitude, longitude) VALUES %s
           ON CONFLICT (nom) DO UPDATE
           SET latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude""",
        VILLES,
    )
    curseur.execute("SELECT nom, id FROM villes")
    return dict(curseur.fetchall())


def charger_meteo(curseur, df, ids_villes):
    """Insère les mesures. Si la ligne (ville, date) existe déjà, on la met à jour."""
    lignes = [
        (
            ids_villes[r.ville], r.date,
            float(r.temp_max), float(r.temp_min), float(r.pluie_mm),
            float(r.temp_moy), bool(r.jour_pluvieux),
        )
        for r in df.itertuples(index=False)
    ]
    execute_values(
        curseur,
        """INSERT INTO meteo_quotidienne
               (ville_id, date, temp_max, temp_min, pluie_mm, temp_moy, jour_pluvieux)
           VALUES %s
           ON CONFLICT (ville_id, date) DO UPDATE SET
               temp_max = EXCLUDED.temp_max, temp_min = EXCLUDED.temp_min,
               pluie_mm = EXCLUDED.pluie_mm, temp_moy = EXCLUDED.temp_moy,
               jour_pluvieux = EXCLUDED.jour_pluvieux""",
        lignes,
    )
    return len(lignes)


def main():
    brut = extraire_tout()
    propre = transformer(brut)

    connexion = connecter()
    try:
        with connexion:                      # valide (commit) tout, ou annule tout en cas d'erreur
            with connexion.cursor() as curseur:
                creer_tables(curseur)
                ids = charger_villes(curseur)
                n = charger_meteo(curseur, propre, ids)
                curseur.execute("SELECT COUNT(*) FROM meteo_quotidienne")
                total = curseur.fetchone()[0]
        print(f"{n} lignes envoyées. La table meteo_quotidienne contient maintenant {total} lignes.")
    finally:
        connexion.close()


if __name__ == "__main__":
    main()