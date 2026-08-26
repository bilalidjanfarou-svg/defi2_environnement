"""
Nettoyage des 6 jeux de donnees du Defi 2 Environnement (Togo AI Lab).

Entree  : data/raw/*.csv (fichiers bruts fournis par le defi)
Sortie  : data/clean/*.csv (fichiers nettoyes, prets pour l'analyse
          et le dashboard)

Usage :
    python notebooks/01_nettoyage.py
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# Indicateurs de la Banque Mondiale pertinents pour le defi.
# (electricite, cuisson, forets, emissions)
INDICATEURS_RETENUS = [
    # Acces electricite
    "Access to electricity (% of population)",
    "Access to electricity, rural (% of rural population)",
    "Access to electricity, urban (% of urban population)",
    # Fiabilite reseau
    "Firms experiencing electrical outages (% of firms)",
    "Power outages in firms in a typical month (number)",
    "Value lost due to electrical outages (% of sales for affected firms)",
    "Cost to get electricity connection (% of income per capita)",
    "Time required to get electricity (days)",
    "Getting electricity (rank)",
    # Cuisson / combustibles
    "Access to clean fuels and technologies for cooking (% of population)",
    "Access to clean fuels and technologies for cooking, rural (% of rural population)",
    "Access to clean fuels and technologies for cooking, urban (% of urban population)",
    "Main cooking fuel: wood (% of households)",
    "Main cooking fuel: charcoal (% of households)",
    "Main cooking fuel: LPG/natural gas/biogas (% of households)",
    "Main cooking fuel: electricity  (% of households)",
    # Forets
    "Forest area (% of land area)",
    "Forest area (sq. km)",
    "Adjusted savings: net forest depletion (% of GNI)",
    "Carbon dioxide (CO2) net fluxes from LULUCF - Deforestation (Mt CO2e)",
    # Energie / emissions secteur energie
    "Renewable energy consumption (% of total final energy consumption)",
    "Carbon dioxide (CO2) emissions from Building (Energy) (Mt CO2e)",
    "Carbon dioxide (CO2) emissions from Power Industry (Energy) (Mt CO2e)",
    "Total greenhouse gas emissions excluding LULUCF (Mt CO2e)",
]


def nettoyer_indicateurs_banque_mondiale() -> pd.DataFrame:
    """Filtre indicators-tgo.csv sur les indicateurs pertinents pour le defi."""
    df = pd.read_csv(RAW_DIR / "indicators-tgo.csv", skiprows=[1])
    df = df[df["Indicator Name"].isin(INDICATEURS_RETENUS)]
    df = df.dropna(subset=["Value"])
    df = df[["Year", "Indicator Name", "Value"]].sort_values(["Indicator Name", "Year"])
    return df.reset_index(drop=True)


def nettoyer_serie_worldbank(nom_fichier: str) -> pd.DataFrame:
    """Nettoie un export World Bank au format long standard
    (date, indicator, value, ...).
    """
    df = pd.read_csv(RAW_DIR / nom_fichier)
    df = df[["date", "indicator", "value"]].dropna(subset=["value"])
    df = df.rename(columns={"date": "Year", "indicator": "Indicator Name", "value": "Value"})
    return df.sort_values("Year").reset_index(drop=True)


def nettoyer_temperatures() -> pd.DataFrame:
    """Charge les temperatures mensuelles (max/min) des 10 villes."""
    df = pd.read_csv(RAW_DIR / "observationdata-yvlucze.csv")
    assert df["villes"].nunique() == 10, "Nombre de villes inattendu"
    return df


def nettoyer_ges_par_secteur() -> pd.DataFrame:
    """Charge les emissions GES par secteur et type de gaz (2018)."""
    return pd.read_csv(RAW_DIR / "observationdata-xorttne.csv")


def nettoyer_forets() -> pd.DataFrame:
    """Charge les forets classees / zones protegees (avec geometrie)."""
    df = pd.read_csv(RAW_DIR / "file-zones-protegees-forets-classees-23-12-2024-09-53-17.csv")
    assert df.isna().sum().sum() == 0, "Valeurs manquantes inattendues"
    return df


def main() -> None:
    etapes = [
        ("indicateurs_electricite_energie_forets.csv", nettoyer_indicateurs_banque_mondiale),
        ("co2_emissions_energie.csv",
         lambda: nettoyer_serie_worldbank("emissions-de-dioxyde-de-carbone-co2-du-secteur-de-lenergie-mt-co2e-.csv")),
        ("energies_renouvelables.csv",
         lambda: nettoyer_serie_worldbank("energies-renouvelables-combustibles-et-dechets-de-lenergie-totale-.csv")),
        ("temperatures_villes.csv", nettoyer_temperatures),
        ("ges_par_secteur_2018.csv", nettoyer_ges_par_secteur),
        ("forets_classees_zones_protegees.csv", nettoyer_forets),
    ]

    for nom_sortie, fonction in etapes:
        df = fonction()
        df.to_csv(CLEAN_DIR / nom_sortie, index=False)
        print(f"{nom_sortie:45s} -> {df.shape[0]:5d} lignes, {df.shape[1]} colonnes")

    print(f"\nNettoyage termine. Fichiers ecrits dans {CLEAN_DIR}/")


if __name__ == "__main__":
    main()