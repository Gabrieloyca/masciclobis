import streamlit as st
from . import analysis
import folium
from streamlit_folium import st_folium

def main():
    st.title("Analyse d'accessibilité urbaine")
    st.markdown("Sélectionnez vos paramètres puis lancez l'analyse.")

    city = st.text_input("Ville", "Paris, France")
    mode = st.selectbox("Mode de déplacement", ["Piéton", "Vélo"])
    radius = st.slider("Rayon d'analyse (km)", 1, 10, 3)

    if st.button("Lancer l'analyse"):
        with st.spinner("Analyse en cours..."):
            gdf, table = analysis.run(city, mode, radius)
        st.success("Analyse terminée ✅")
        
        # Carte
        m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)
        folium.GeoJson(gdf).add_to(m)
        st_folium(m, width=700, height=500)

        st.dataframe(table)

        st.download_button("Télécharger GeoJSON", gdf.to_json(), "resultats.geojson")
        st.download_button("Télécharger CSV", table.to_csv(index=False), "resultats.csv")
        
        if st.button("↩ Rejouer"):
            st.experimental_rerun()