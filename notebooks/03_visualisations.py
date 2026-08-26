"""
Premieres visualisations pour le tableau de bord.

Entree  : data/clean/*.csv
Sortie  : reports/figures/*.png (graphiques exportes en image)

Usage :
    python notebooks/03_visualisations.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CLEAN_DIR = Path("data/clean")
FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.size"] = 10


def graphique_electrification_ville_campagne() -> None:
    """Evolution comparee acces electricite urbain vs rural."""
    df = pd.read_csv(CLEAN_DIR / "indicateurs_electricite_energie_forets.csv")

    fig, ax = plt.subplots(figsize=(8, 5))
    for label, indicateur, couleur in [
        ("Urbain", "Access to electricity, urban (% of urban population)", "#1f77b4"),
        ("Rural", "Access to electricity, rural (% of rural population)", "#d62728"),
        ("National", "Access to electricity (% of population)", "#2ca02c"),
    ]:
        serie = df[df["Indicator Name"] == indicateur].sort_values("Year")
        ax.plot(serie["Year"], serie["Value"], marker="o", label=label, color=couleur)

    ax.set_title("Acces a l'electricite au Togo : ville vs campagne")
    ax.set_xlabel("Annee")
    ax.set_ylabel("% de la population")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "electrification_ville_campagne.png")
    plt.close(fig)


def graphique_combustibles_cuisson() -> None:
    """Repartition des combustibles de cuisson (derniere annee disponible)."""
    df = pd.read_csv(CLEAN_DIR / "indicateurs_electricite_energie_forets.csv")

    combustibles = {
        "Bois": "Main cooking fuel: wood (% of households)",
        "Charbon": "Main cooking fuel: charcoal (% of households)",
        "Gaz/LPG": "Main cooking fuel: LPG/natural gas/biogas (% of households)",
    }
    valeurs, labels = [], []
    for label, indicateur in combustibles.items():
        sous_df = df[df["Indicator Name"] == indicateur]
        if not sous_df.empty:
            valeurs.append(sous_df.iloc[-1]["Value"])
            labels.append(label)

    fig, ax = plt.subplots(figsize=(6, 5))
    couleurs = ["#8B4513", "#4d4d4d", "#2ca02c"]
    ax.bar(labels, valeurs, color=couleurs[: len(labels)])
    ax.set_title("Principal combustible de cuisson des menages")
    ax.set_ylabel("% des menages")
    for i, v in enumerate(valeurs):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "combustibles_cuisson.png")
    plt.close(fig)


def graphique_emissions_par_secteur() -> None:
    """Repartition des emissions GES par secteur (2018)."""
    df = pd.read_csv(CLEAN_DIR / "ges_par_secteur_2018.csv")
    df_secteurs = df[df["secteur"] != "Total"]
    par_secteur = df_secteurs.groupby("secteur")["Value"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.pie(
        par_secteur.values,
        labels=par_secteur.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#556B2F", "#d62728", "#7f7f7f", "#1f77b4"],
    )
    ax.set_title("Emissions de gaz a effet de serre par secteur (2018)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "emissions_par_secteur.png")
    plt.close(fig)


def graphique_temperatures_par_ville() -> None:
    """Temperature maximale moyenne par ville, du Sud au Nord."""
    df = pd.read_csv(CLEAN_DIR / "temperatures_villes.csv")
    df_max = df[df["libellés"] == "Températures maximales"]
    moyenne_par_ville = df_max.groupby("villes")["Value"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(moyenne_par_ville.index, moyenne_par_ville.values, color="#ff7f0e")
    ax.set_title("Temperature maximale moyenne par ville (2013-2019)")
    ax.set_xlabel("Temperature (degres C)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "temperatures_par_ville.png")
    plt.close(fig)


def main() -> None:
    graphique_electrification_ville_campagne()
    graphique_combustibles_cuisson()
    graphique_emissions_par_secteur()
    graphique_temperatures_par_ville()
    print(f"4 graphiques generes dans {FIG_DIR}/")


if __name__ == "__main__":
    main()