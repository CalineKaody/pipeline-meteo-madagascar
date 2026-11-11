"""
Tableau de bord météo de Madagascar (Streamlit).
Lit les données dans PostgreSQL (remplies par load.py) et les affiche.
Lancement :  streamlit run app.py
"""
import pandas as pd
import streamlit as st
from load import connecter   # on réutilise la connexion (identifiants lus dans .env)

st.set_page_config(page_title="Météo Madagascar", layout="wide")
st.title("Météo de huit villes de Madagascar")
st.caption("Source : Open-Meteo. Pipeline Python, base PostgreSQL, tableau de bord Streamlit.")

REQUETE = """
SELECT v.nom AS ville, m.date, m.temp_max, m.temp_min, m.temp_moy, m.pluie_mm, m.jour_pluvieux
FROM meteo_quotidienne m
JOIN villes v ON v.id = m.ville_id
ORDER BY m.date, v.nom
"""


@st.cache_data(ttl=300)   # garde le résultat 5 minutes pour ne pas interroger la base à chaque clic
def charger_donnees():
    connexion = connecter()
    try:
        with connexion.cursor() as curseur:
            curseur.execute(REQUETE)
            colonnes = [c[0] for c in curseur.description]
            df = pd.DataFrame(curseur.fetchall(), columns=colonnes)
    finally:
        connexion.close()
    for c in ["temp_max", "temp_min", "temp_moy", "pluie_mm"]:
        df[c] = df[c].astype(float)     # NUMERIC de PostgreSQL -> nombres Python
    df["date"] = pd.to_datetime(df["date"])
    return df


df = charger_donnees()
if df.empty:
    st.warning("La base est vide. Lancez d'abord : python load.py")
    st.stop()

villes = sorted(df["ville"].unique())
choix = st.sidebar.multiselect("Villes", villes, default=villes)
d = df[df["ville"].isin(choix)]
if d.empty:
    st.info("Choisissez au moins une ville dans le menu de gauche.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Villes affichées", d["ville"].nunique())
col2.metric("Température moyenne", f"{d['temp_moy'].mean():.1f} °C")
col3.metric("Pluie totale", f"{d['pluie_mm'].sum():.1f} mm")

st.subheader("Température maximale par jour")
st.line_chart(d.pivot(index="date", columns="ville", values="temp_max"))

gauche, droite = st.columns(2)
with gauche:
    st.subheader("Température moyenne par ville")
    st.bar_chart(d.groupby("ville")["temp_moy"].mean().round(1))
with droite:
    st.subheader("Pluie totale par ville (mm)")
    st.bar_chart(d.groupby("ville")["pluie_mm"].sum())

st.subheader("Données")
st.dataframe(d.assign(date=d["date"].dt.date), use_container_width=True, hide_index=True)
