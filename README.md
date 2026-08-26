# Defi 2 — Environnement | Togo AI Lab

Tableau de bord et analyses pour le defi "Environnement | Defi 2" du
Laboratoire d'IA du Togo (Energie & transition ecologique au Togo).

## Sujet

Analyser l'acces a l'electricite, la dependance aux combustibles de
cuisson (bois, charbon), les emissions du secteur energie et la
localisation des forets classees/zones protegees, pour proposer des
solutions concretes d'electrification rurale, d'energies propres et
de protection des forets.

## Lancer le tableau de bord

pip install -r requirements.txt
streamlit run dashboard/app.py

L'application s'ouvre automatiquement dans le navigateur a l'adresse
http://localhost:8501

## Structure du projet

data/
raw/ donnees brutes fournies par le defi (6 fichiers)
clean/ donnees nettoyees, pretes a l'analyse
notebooks/ scripts de nettoyage et de calcul des indicateurs
dashboard/ application Streamlit (tableau de bord interactif)
reports/ rapport PowerPoint et figures
requirements.txt dependances Python


## Points cles de l'analyse

- Ecart d'electrification ville/campagne : 71,5 points (96,5 % urbain
  vs 25 % rural, 2022)
- 89,4 % des menages cuisinent au bois ou au charbon
- Le secteur AFAT (agriculture, foret, terres) represente 87,7 % des
  emissions de GES du pays, contre 6,2 % pour l'energie
- 53 forets classees, tres inegalement reparties (20 dans les
  Plateaux contre 4 dans les Savanes)

## Livrables

- Tableau de bord interactif : `dashboard/app.py` (Streamlit)
- Rapport : `reports/final/defi2_environnement_rapport.pptx`