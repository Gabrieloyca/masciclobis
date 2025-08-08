# Application d’analyse d’accessibilité

Ce dépôt contient une application web qui permet de télécharger et
d’analyser des réseaux de transport urbain. À partir d’un nom de ville
et de quelques paramètres simples, l’app calcule des indicateurs
d’accessibilité et affiche le réseau sur une carte interactive. Les
résultats peuvent être téléchargés aux formats GeoJSON, CSV et PDF.

## Prérequis

- Python ≥ 3.10
- [Docker](https://docs.docker.com/) (optionnel, pour un déploiement en un clic)

## Installation locale

1. Clonez ce dépôt :

   ```bash
   git clone <URL_DE_VOTRE_DÉPÔT>
   cd <nom_du_dossier>
   ```

2. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

3. Lancez l’application :

   ```bash
   streamlit run app/main.py
   ```

4. Ouvrez votre navigateur à l’adresse affichée (par défaut
   <http://localhost:8501>). Entrez le nom d’une ville et cliquez sur
   « Lancer l’analyse ».

## Utilisation via Docker

Pour éviter d’installer Python et les bibliothèques manuellement, vous
pouvez utiliser Docker :

```bash
docker build -t grafos-app .
docker run -p 8501:8501 grafos-app
```

L’application sera disponible sur <http://localhost:8501>.

## Fonctionnalités

- **Recherche de ville** : saisissez un nom de ville pour centrer
  l’analyse. La géocodage utilise [Nominatim](https://nominatim.openstreetmap.org/).
- **Choix du mode de déplacement** : à pied ou à vélo.
- **Rayon d’analyse** : sélectionnez la distance autour du centre-ville
  (de 1 à 10 km).
- **Indicateurs** : nombre de nœuds, nombre d’arêtes, longueur totale du
  réseau (km). D’autres indicateurs peuvent être ajoutés facilement.
- **Carte interactive** : le réseau est affiché sur une carte
  interactive grâce à Folium. Vous pouvez zoomer et déplacer la carte.
- **Téléchargements** : exportez le réseau au format GeoJSON ou CSV, et
  générez un rapport PDF de synthèse.

## Déploiement en ligne

L’application est conçue pour être déployée facilement sur des
plateformes telles que [Streamlit Cloud](https://streamlit.io/cloud)
ou [Hugging Face Spaces](https://huggingface.co/spaces/). Les étapes
générales sont :

1. Créez un nouveau projet sur la plateforme de votre choix.
2. Chargez les fichiers de ce dépôt.
3. Spécifiez la commande de démarrage `streamlit run app/main.py`.
4. Ajoutez la variable d’environnement `MAPBOX_TOKEN` si vous
   utilisez Mapbox (optionnel).
5. Lancez le déploiement. La plateforme fournira une URL publique
   accessible sans installation.

## Exemple

Le dépôt inclut un petit dataset d’exemple dans le dossier `data/`
(s’il existe). Pour tester l’application hors ligne, vous pouvez
modifier `app/utils.py` pour charger ces données au lieu de
télécharger depuis OpenStreetMap.

## Avertissement

Cette application effectue des appels réseau vers les services OSM
(géocodage Nominatim et téléchargement du réseau). Assurez‑vous de
respecter les conditions d’utilisation d’OpenStreetMap et d’éviter les
requêtes en masse.
