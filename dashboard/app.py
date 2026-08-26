"""
Tableau de bord interactif - Defi 2 Environnement (Togo AI Lab).

Usage :
    streamlit run dashboard/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

CLEAN_DIR = Path(__file__).resolve().parent.parent / "data" / "clean"

st.set_page_config(
    page_title="Defi 2 Environnement - Togo AI Lab",
    page_icon="🌍",
    layout="wide",
)


@st.cache_data
def charger_donnees():
    indicateurs = pd.read_csv(CLEAN_DIR / "indicateurs_electricite_energie_forets.csv")
    temperatures = pd.read_csv(CLEAN_DIR / "temperatures_villes.csv")
    ges = pd.read_csv(CLEAN_DIR / "ges_par_secteur_2018.csv")
    forets = pd.read_csv(CLEAN_DIR / "forets_classees_zones_protegees.csv")
    kpis = pd.read_csv(CLEAN_DIR / "kpis_resume.csv")
    return indicateurs, temperatures, ges, forets, kpis


indicateurs, temperatures, ges, forets, kpis = charger_donnees()

# -----------------------------------------------------------------
# En-tete
# -----------------------------------------------------------------
st.title("🌍 Energie & transition ecologique au Togo")
st.caption("Defi 2 Environnement - Laboratoire d'IA du Togo")

onglets = st.tabs([
    "⚡ Electricite",
    "🔥 Cuisson & combustibles",
    "🌫️ Emissions & climat",
    "🌳 Forets",
    "💡 Recommandations",
])

# -----------------------------------------------------------------
# Onglet 1 : Electricite
# -----------------------------------------------------------------
with onglets[0]:
    st.subheader("Acces a l'electricite : un fort contraste ville / campagne")

    col1, col2, col3 = st.columns(3)
    col1.metric("Acces national", "57.2 %", help="2022")
    col2.metric("Acces urbain", "96.5 %", help="2022")
    col3.metric("Acces rural", "25.0 %", "-71.5 pts vs urbain", delta_color="inverse")

    indics_elec = [
        "Access to electricity (% of population)",
        "Access to electricity, urban (% of urban population)",
        "Access to electricity, rural (% of rural population)",
    ]
    df_elec = indicateurs[indicateurs["Indicator Name"].isin(indics_elec)]
    fig = px.line(
        df_elec, x="Year", y="Value", color="Indicator Name", markers=True,
        labels={"Value": "% de la population", "Year": "Annee", "Indicator Name": "Zone"},
        title="Evolution de l'acces a l'electricite (1990-2022)",
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------
# Onglet 2 : Cuisson
# -----------------------------------------------------------------
with onglets[1]:
    st.subheader("Une tres large majorite des menages cuisine encore au bois ou au charbon")

    combustibles = {
        "Bois": "Main cooking fuel: wood (% of households)",
        "Charbon": "Main cooking fuel: charcoal (% of households)",
        "Gaz/LPG": "Main cooking fuel: LPG/natural gas/biogas (% of households)",
    }
    lignes = []
    for label, code in combustibles.items():
        sous = indicateurs[indicateurs["Indicator Name"] == code]
        if not sous.empty:
            lignes.append({"Combustible": label, "Part": sous.iloc[-1]["Value"]})
    df_combustibles = pd.DataFrame(lignes)

    fig = px.bar(
        df_combustibles, x="Combustible", y="Part", color="Combustible",
        text_auto=".1f", title="Principal combustible de cuisson des menages (2017)",
        labels={"Part": "% des menages"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.info("89.4 % des menages cuisinent au bois ou au charbon, contre seulement "
            "11.9 % ayant acces a des combustibles propres au niveau national.")

# -----------------------------------------------------------------
# Onglet 3 : Emissions & climat
# -----------------------------------------------------------------
with onglets[2]:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Emissions de GES par secteur (2018)")
        ges_secteurs = ges[ges["secteur"] != "Total"]
        par_secteur = ges_secteurs.groupby("secteur", as_index=False)["Value"].sum()
        fig = px.pie(
            par_secteur, names="secteur", values="Value",
            title="Repartition des emissions par secteur",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Le secteur AFAT (agriculture, foresterie, terres) domine largement "
                    "les emissions - l'energie ne represente que 6.2 %.")

    with col2:
        st.subheader("Temperatures maximales par ville (2013-2019)")
        temp_max = temperatures[temperatures["libellés"] == "Températures maximales"]
        moyenne = temp_max.groupby("villes", as_index=False)["Value"].mean().sort_values("Value")
        fig = px.bar(
            moyenne, x="Value", y="villes", orientation="h",
            labels={"Value": "Temperature (°C)", "villes": ""},
            title="Temperature maximale moyenne par ville",
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------
# Onglet 4 : Forets
# -----------------------------------------------------------------
with onglets[3]:
    st.subheader("53 forets classees et zones protegees")

    col1, col2 = st.columns([1, 2])
    with col1:
        par_region = forets["region_nom_bdd"].value_counts().reset_index()
        par_region.columns = ["Region", "Nombre de forets"]
        fig = px.bar(
            par_region, x="Region", y="Nombre de forets", color="Region",
            title="Nombre de forets classees par region",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            forets[["etab_nom", "region_nom_bdd", "prefecture_nom_bdd", "etab_creation_date"]]
            .rename(columns={
                "etab_nom": "Foret / zone",
                "region_nom_bdd": "Region",
                "prefecture_nom_bdd": "Prefecture",
                "etab_creation_date": "Annee de creation",
            }),
            use_container_width=True, height=400,
        )

# -----------------------------------------------------------------
# Onglet 5 : Recommandations
# -----------------------------------------------------------------
with onglets[4]:
    st.subheader("Recommandations")
    st.markdown("""
- **Prioriser l'electrification rurale par solaire decentralise** dans les regions
  ou l'ecart ville/campagne est le plus fort, en particulier autour des zones
  forestieres vulnerables (Savanes, Kara).
- **Promouvoir les foyers de cuisson ameliores et le gaz domestique (LPG)**
  pour reduire la pression sur les forets liee au bois/charbon (89.4 % des menages).
- **Cibler les zones proches des 53 forets classees** en priorite pour les
  programmes d'acces a l'energie propre, afin de limiter la deforestation.
- **Ne pas confondre biomasse traditionnelle et energie renouvelable propre** :
  le chiffre de 75.1 % d'"energies renouvelables" est en grande partie du bois/
  charbon, pas du solaire ou de l'hydraulique.
""")