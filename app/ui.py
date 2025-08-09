
import streamlit as st
from . import analysis, map as map_mod
from streamlit_folium import st_folium

def run():
    st.title("Analyse d’accessibilité urbaine")
    st.caption("Sélectionnez une ville, des paramètres et lancez l’analyse.")

    with st.form("params"):
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            city = st.text_input("Ville (ex.: 'Monaco, Monaco' ou 'Paris, France')", "Monaco, Monaco")
        with col2:
            mode = st.selectbox("Profil", ["walk", "bike"], index=0, help="Type de réseau OpenStreetMap")
        with col3:
            radius_km = st.slider("Rayon (km)", 0.2, 5.0, 1.0, 0.1)

        c1, c2, c3 = st.columns(3)
        with c1:
            do_centrality = st.checkbox("Centralité (betweenness)", True)
        with c2:
            do_h3 = st.checkbox("Agrégation H3 (longueur par hex)", True)
        with c3:
            h3_res = st.slider("Résolution H3", 6, 9, 7)

        submitted = st.form_submit_button("Lancer l’analyse", use_container_width=True)

    if not submitted:
        st.info("Renseignez les paramètres puis lancez l’analyse.")
        return

    with st.spinner("Téléchargement OSM & calculs…"):
        result = analysis.run(
            city=city,
            mode=mode,
            radius_km=radius_km,
            do_centrality=do_centrality,
            do_h3=do_h3,
            h3_res=h3_res,
        )

    if result.get("error"):
        st.error(result["error"])
        if result.get("trace"):
            with st.expander("Trace technique"):
                st.code(result["trace"])
        return

    st.success("Analyse terminée ✅")

    m = result["metrics"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Noeuds", f"{m.get('nodes', 0):,}".replace(",", " "))
    k2.metric("Arêtes", f"{m.get('edges', 0):,}".replace(",", " "))
    k3.metric("Longueur réseau (km)", f"{m.get('total_km', 0):.2f}")
    k4.metric("Composantes", f"{m.get('components', 0)}")

    folium_map = map_mod.build_map(result)
    st_folium(folium_map, height=600, use_container_width=True)

    if "metrics_df" in result and not result["metrics_df"].empty:
        st.subheader("Indicateurs détaillés")
        st.dataframe(result["metrics_df"], use_container_width=True)

    st.subheader("Téléchargements")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button(
            "GeoJSON — réseau",
            data=result["edges_geojson"].encode("utf-8"),
            file_name="reseau.geojson",
            mime="application/geo+json",
            use_container_width=True,
        )
    with dcol2:
        st.download_button(
            "CSV — indicateurs",
            data=result["metrics_csv"].encode("utf-8"),
            file_name="indicateurs.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if result.get("h3_geojson"):
        st.download_button(
            "GeoJSON — H3 agrégé",
            data=result["h3_geojson"].encode("utf-8"),
            file_name="h3.geojson",
            mime="application/geo+json",
            use_container_width=True,
        )

    st.divider()
    if st.button("↩ Rejouer avec d’autres paramètres", type="secondary"):
        st.experimental_rerun()
