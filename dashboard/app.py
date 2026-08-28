"""
Tableau de bord interactif - Defi 2 Environnement (Togo AI Lab).

Usage :
    streamlit run dashboard/app.py
"""

import folium
from shapely import wkt
from streamlit_folium import st_folium
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

st.markdown("""
<style>
/* En-tete avec bandeau degrade */
.main-header {
    background: linear-gradient(135deg, #1b4332 0%, #2ca02c 50%, #f4a261 100%);
    padding: 1.8rem 3rem;
    margin-bottom: 1.5rem;
    color: white;
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
    border-radius: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 110px;
}
.main-header h1 {
    color: white;
    margin: 0;
    font-size: 1.7rem;
    font-weight: 700;
    line-height: 1.3;
}
.main-header p {
    color: #e8f5e9;
    margin: 0.4rem 0 0 0;
    font-size: 0.95rem;
}
div.block-container {
    padding-top: 1rem;
}
/* Cartes metriques */
div[data-testid="stMetric"] {
    background-color: #f8f9f5;
    border: 1px solid #d4e0d0;
    border-left: 4px solid #2ca02c;
    border-radius: 8px;
    padding: 1rem 1.2rem;
}
div[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: #4a4a4a;
}

/* Onglets */
div[data-baseweb="tab-list"] {
    gap: 4px;
    background-color: #f0f2e9;
    padding: 6px;
    border-radius: 10px;
}
button[data-baseweb="tab"] {
    font-size: 1.0rem;
    font-weight: 600;
    color: #4a4a4a;
    border-radius: 8px;
    padding: 0.5rem 1rem;
}
button[data-baseweb="tab"]:hover {
    background-color: #e0e8dc;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #2ca02c;
    color: white !important;
}
div[data-baseweb="tab-highlight"] {
    display: none;
}

/* Encarts info */
div[data-testid="stAlert"] {
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


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
# Sidebar - Filtres
# -----------------------------------------------------------------
st.sidebar.caption("Affinez les analyses par region, ville et periode.")

toutes_regions = sorted(forets["region_nom_bdd"].unique())
regions_selectionnees = st.sidebar.multiselect(
    "Region (forets)", options=toutes_regions, default=toutes_regions,
)

toutes_villes = sorted(temperatures["villes"].unique())
villes_selectionnees = st.sidebar.multiselect(
    "Ville (temperatures)", options=toutes_villes, default=toutes_villes,
)

if st.sidebar.button("Reinitialiser les filtres"):
    st.rerun()

# Dataframes filtres, utilises dans les onglets Forets et Emissions/Climat

forets_filtre = forets[forets["region_nom_bdd"].isin(regions_selectionnees)]
temperatures_filtre = temperatures[temperatures["villes"].isin(villes_selectionnees)]

annee_min, annee_max = st.sidebar.slider(
    "Periode (electrification)",
    min_value=1998, max_value=2022, value=(1998, 2022),
)

# -----------------------------------------------------------------
# En-tete
# -----------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🌍 Energie & transition ecologique au Togo</h1>
    <p>Defi 2 Environnement — Laboratoire d'IA du Togo</p>
</div>
""", unsafe_allow_html=True)

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
    df_elec = df_elec[df_elec["Year"].between(annee_min, annee_max)]
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
        st.subheader("Temperatures par ville (2013-2019)")

        type_temp = st.radio(
            "Afficher", ["Maximales", "Minimales"], horizontal=True, key="type_temp",
        )
        libelle = f"Températures {type_temp.lower()}"

        temp_choisie = temperatures_filtre[temperatures_filtre["libellés"] == libelle]
        moyenne = temp_choisie.groupby("villes", as_index=False)["Value"].mean().sort_values("Value")
        fig = px.bar(
            moyenne, x="Value", y="villes", orientation="h",
            labels={"Value": "Temperature (°C)", "villes": ""},
            title=f"Temperature {type_temp.lower()} moyenne par ville",
            color_discrete_sequence=["#E07A29"] if type_temp == "Maximales" else ["#4A90D9"],
        )
        st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------
# Onglet 4 : Forets
# -----------------------------------------------------------------
with onglets[3]:
    st.subheader(f"Forets classees et zones protegees ({len(forets_filtre)} sur 53)")

    col1, col2 = st.columns([1, 2])
    with col1:
        par_region = forets_filtre["region_nom_bdd"].value_counts().reset_index()
        par_region.columns = ["Region", "Nombre de forets"]
        fig = px.bar(
            par_region, x="Region", y="Nombre de forets", color="Region",
            title="Nombre de forets classees par region",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            forets_filtre[["etab_nom", "region_nom_bdd", "prefecture_nom_bdd", "etab_creation_date"]]
            .rename(columns={
                "etab_nom": "Foret / zone",
                "region_nom_bdd": "Region",
                "prefecture_nom_bdd": "Prefecture",
                "etab_creation_date": "Annee de creation",
            }),
            use_container_width=True, height=400,
        )

    st.markdown("#### Carte des forets classees et zones protegees")

    couleurs_region = {
        "Maritime": "#1f77b4",
        "Plateaux": "#2ca02c",
        "Centrale": "#ff7f0e",
        "Kara": "#9467bd",
        "Savanes": "#d62728",
    }

    carte = folium.Map(location=[8.6, 1.0], zoom_start=7, tiles="OpenStreetMap")

    for _, ligne in forets_filtre.iterrows():
        try:
            geometrie = wkt.loads(ligne["geometry"])
            couleur = couleurs_region.get(ligne["region_nom_bdd"], "#808080")

            geojson_layer = folium.GeoJson(
                geometrie.__geo_interface__,
                style_function=lambda feature, c=couleur: {
                    "fillColor": c,
                    "color": c,
                    "weight": 1.5,
                    "fillOpacity": 0.4,
                },
                tooltip=f"{ligne['etab_nom']} ({ligne['region_nom_bdd']})",
            )
            geojson_layer.add_to(carte)
        except Exception:
            continue
    st_folium(carte, use_container_width=True, height=500)

    st.download_button(
        "Telecharger les forets filtrees (CSV)",
        data=forets_filtre.to_csv(index=False).encode("utf-8"),
        file_name="forets_filtrees.csv",
        mime="text/csv",
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