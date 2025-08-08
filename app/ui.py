"""User interface definition for the accessibility web app.

This module builds the Streamlit UI which allows end users to search
for cities, adjust analysis parameters, run computations and view
results. It also provides download buttons for the computed data and
report. The interface is entirely in French and is designed to be
usable by non-technical users.
"""

from __future__ import annotations

import io
import os
import tempfile
from datetime import datetime

import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from app import analysis, map as map_module, utils
from grafos import export


def run() -> None:
    """Render the Streamlit user interface and handle interactions."""
    st.set_page_config(
        page_title="Analyse d'accessibilité", layout="wide", initial_sidebar_state="expanded"
    )
    st.title("Analyse d'accessibilité des réseaux urbains")
    st.markdown(
        "Cette application permet de sélectionner une ville, de choisir des paramètres "
        "d’analyse (mode de déplacement et rayon) et de visualiser les métriques d’accessibilité sur une carte interactive."
    )

    with st.sidebar:
        st.header("Paramètres")
        city = st.text_input(
            "Ville (ex : Paris, France)", value="Paris, France", help="Entrez le nom de la ville à analyser"
        )
        mode = st.selectbox(
            "Mode de déplacement",
            options=["walk", "bike"],
            format_func=lambda x: "À pied" if x == "walk" else "À vélo",
        )
        radius_km = st.slider(
            "Rayon d’analyse (km)",
            min_value=1,
            max_value=10,
            value=2,
            step=1,
            help="Rayon en kilomètres autour du centre-ville à inclure dans l’analyse",
        )
        run_button = st.button("Lancer l’analyse", type="primary")

    if run_button:
        # Convert radius to metres
        radius_m = int(radius_km * 1000)
        try:
            with st.spinner("Téléchargement du réseau et calcul des indicateurs…"):
                metrics_dict, G, gdf_edges = analysis.run_analysis(city, mode, radius_m)
        except Exception as e:
            st.error(f"Erreur lors de l'analyse : {e}")
            return

        # Display metrics
        st.subheader("Indicateurs principaux")
        df_metrics = pd.DataFrame(
            {
                "Métrique": list(metrics_dict.keys()),
                "Valeur": list(metrics_dict.values()),
            }
        )
        st.dataframe(df_metrics, hide_index=True)

        # Display map
        st.subheader("Réseau accessible")
        folium_map = map_module.make_map(gdf_edges)
        # Render map in Streamlit
        st_folium(
            folium_map,
            width=1000,
            height=600,
            returned_objects=[],
            use_container_width=True,
        )

        # Provide downloads
        st.subheader("Téléchargements")
        # Create temporary files for download
        tmpdir = tempfile.mkdtemp()
        geojson_path = os.path.join(tmpdir, "reseau.geojson")
        csv_path = os.path.join(tmpdir, "reseau.csv")
        pdf_path = os.path.join(tmpdir, "rapport.pdf")

        # Export GeoJSON and CSV
        export.export_geojson(gdf_edges, geojson_path)
        export.export_csv(gdf_edges, csv_path)

        # Capture map as PNG for PDF
        # Use _to_png method provided by folium Map to obtain image bytes
        try:
            map_png = folium_map._to_png(5)
            map_image_path = os.path.join(tmpdir, "map.png")
            with open(map_image_path, "wb") as f:
                f.write(map_png)
        except Exception:
            map_image_path = None

        # Export PDF report
        export.export_pdf(metrics_dict, city, pdf_path, map_path=map_image_path)

        # Read files for download buttons
        with open(geojson_path, "rb") as f:
            geojson_bytes = f.read()
        with open(csv_path, "rb") as f:
            csv_bytes = f.read()
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            "Télécharger GeoJSON", data=geojson_bytes, file_name="reseau.geojson", mime="application/geo+json"
        )
        st.download_button(
            "Télécharger CSV", data=csv_bytes, file_name="reseau.csv", mime="text/csv"
        )
        st.download_button(
            "Télécharger PDF", data=pdf_bytes, file_name="rapport.pdf", mime="application/pdf"
        )
