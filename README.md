
# Application d’analyse d’accessibilité (cloud-ready)

Cette app calcule et cartographie des indicateurs d’accessibilité à partir d’OpenStreetMap :
- Réseau piéton/vélo sur un rayon autour d’une ville
- Centralité (betweenness) approximée
- Agrégation H3 (longueur de réseau par hexagone)
- Téléchargements GeoJSON / CSV
- Interface en français, PDF désactivé (pas de dépendances système)

## Déploiement Streamlit Cloud
1) Uploadez le contenu de ce dossier dans votre repo GitHub.
2) Dans Streamlit Cloud, configurez `Main file path` = `streamlit_app.py`.
3) Lancez le déploiement.

## Exécution locale
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
