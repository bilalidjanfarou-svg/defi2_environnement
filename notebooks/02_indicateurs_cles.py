"""
Calcul des indicateurs cles (KPI) pour le tableau de bord.

Entree  : data/clean/*.csv
Sortie  : data/clean/kpis_resume.csv (tableau recapitulatif)

Usage :
    python notebooks/02_indicateurs_cles.py
"""
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")


def derniere_valeur(df: pd.DataFrame, indicateur: str) -> tuple[float, int] | None:
    """Retourne (valeur, annee) la plus recente disponible pour un indicateur."""
    sous_df = df[df["Indicator Name"] == indicateur].sort_values("Year")
    if sous_df.empty:
        return None
    ligne = sous_df.iloc[-1]
    return ligne["Value"], int(ligne["Year"])


def kpi_electrification(df: pd.DataFrame) -> list[dict]:
    """Ecart d'electrification ville / campagne."""
    kpis = []
    for label, indicateur in [
        ("Acces electricite - national (%)", "Access to electricity (% of population)"),
        ("Acces electricite - urbain (%)", "Access to electricity, urban (% of urban population)"),
        ("Acces electricite - rural (%)", "Access to electricity, rural (% of rural population)"),
    ]:
        resultat = derniere_valeur(df, indicateur)
        if resultat:
            valeur, annee = resultat
            kpis.append({"KPI": label, "Valeur": round(valeur, 1), "Annee": annee})

    urbain = derniere_valeur(df, "Access to electricity, urban (% of urban population)")
    rural = derniere_valeur(df, "Access to electricity, rural (% of rural population)")
    if urbain and rural:
        kpis.append({
            "KPI": "Ecart electrification ville - campagne (points)",
            "Valeur": round(urbain[0] - rural[0], 1),
            "Annee": max(urbain[1], rural[1]),
        })
    return kpis


def kpi_cuisson(df: pd.DataFrame) -> list[dict]:
    """Poids des combustibles de cuisson traditionnels vs propres."""
    kpis = []
    for label, indicateur in [
        ("Cuisson au bois (% menages)", "Main cooking fuel: wood (% of households)"),
        ("Cuisson au charbon (% menages)", "Main cooking fuel: charcoal (% of households)"),
        ("Cuisson au gaz/LPG (% menages)", "Main cooking fuel: LPG/natural gas/biogas (% of households)"),
        ("Acces combustibles propres - national (%)",
         "Access to clean fuels and technologies for cooking (% of population)"),
    ]:
        resultat = derniere_valeur(df, indicateur)
        if resultat:
            valeur, annee = resultat
            kpis.append({"KPI": label, "Valeur": round(valeur, 1), "Annee": annee})
    return kpis


def kpi_forets_energie(df: pd.DataFrame) -> list[dict]:
    """Forets et part des energies renouvelables."""
    kpis = []
    for label, indicateur in [
        ("Superficie forestiere (% du territoire)", "Forest area (% of land area)"),
        ("Energies renouvelables (% conso finale)",
         "Renewable energy consumption (% of total final energy consumption)"),
    ]:
        resultat = derniere_valeur(df, indicateur)
        if resultat:
            valeur, annee = resultat
            kpis.append({"KPI": label, "Valeur": round(valeur, 1), "Annee": annee})
    return kpis


def kpi_emissions_ges() -> list[dict]:
    """Poids du secteur energie dans les emissions totales (2018)."""
    df = pd.read_csv(CLEAN_DIR / "ges_par_secteur_2018.csv")

    # La ligne "Total" est deja un total, on l'exclut du calcul
    # des parts sectorielles pour eviter de compter deux fois.
    df_secteurs = df[df["secteur"] != "Total"]
    total = df_secteurs["Value"].sum()
    par_secteur = df_secteurs.groupby("secteur")["Value"].sum().sort_values(ascending=False)

    kpis = []
    for secteur, valeur in par_secteur.items():
        kpis.append({
            "KPI": f"Emissions GES - secteur {secteur} (part du total, %)",
            "Valeur": round(100 * valeur / total, 1),
            "Annee": 2018,
        })
    return kpis


def kpi_temperatures() -> list[dict]:
    """Ecart de temperature max entre la ville la plus au sud et la plus au nord."""
    df = pd.read_csv(CLEAN_DIR / "temperatures_villes.csv")
    df_max = df[df["libellés"] == "Températures maximales"]
    moyenne_par_ville = df_max.groupby("villes")["Value"].mean().sort_values(ascending=False)

    return [{
        "KPI": f"Temperature max moyenne la plus elevee : {moyenne_par_ville.index[0]}",
        "Valeur": round(moyenne_par_ville.iloc[0], 1),
        "Annee": "2013-2019",
    }, {
        "KPI": f"Temperature max moyenne la plus basse : {moyenne_par_ville.index[-1]}",
        "Valeur": round(moyenne_par_ville.iloc[-1], 1),
        "Annee": "2013-2019",
    }]


def main() -> None:
    df_indicateurs = pd.read_csv(CLEAN_DIR / "indicateurs_electricite_energie_forets.csv")

    tous_les_kpis = (
        kpi_electrification(df_indicateurs)
        + kpi_cuisson(df_indicateurs)
        + kpi_forets_energie(df_indicateurs)
        + kpi_emissions_ges()
        + kpi_temperatures()
    )

    df_resume = pd.DataFrame(tous_les_kpis)
    df_resume.to_csv(CLEAN_DIR / "kpis_resume.csv", index=False)

    print(df_resume.to_string(index=False))
    print(f"\n{len(df_resume)} KPIs calcules -> data/clean/kpis_resume.csv")


if __name__ == "__main__":
    main()