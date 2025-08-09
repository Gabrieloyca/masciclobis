import streamlit as st
from . import analysis, map as map_mod
from streamlit_folium import st_folium

def run():
    st.title("Accessibilité urbaine — Analyse de graphes")
    if "result" not in st.session_state:
        st.session_state.result = None

    with st.form("params", clear_on_submit=False):
        c1, c2, c3 = st.columns([2,1,1])
        with c1:
            city = st.text_input("Ville", "Monaco, Monaco")
        with c2:
            mode = st.selectbox("Profil OSM", ["walk","bike"], index=0)
        with c3:
            radius_km = st.slider("Rayon (km)", 0.2, 5.0, 1.0, 0.1)

        c4, c5, c6 = st.columns(3)
        with c4:
            do_centrality = st.checkbox("Betweenness", True)
        with c5:
            do_closeness = st.checkbox("Closeness", False)
        with c6:
            do_degree = st.checkbox("Degré", False)

        c7, c8 = st.columns([1,1])
        with c7:
            do_h3 = st.checkbox("Agrégation H3", True)
        with c8:
            h3_res = st.slider("Résolution H3", 6, 9, 7)

        color_by = st.selectbox("Colorer par", ["betweenness","length","closeness","degree"])
        submitted = st.form_submit_button("Lancer l’analyse", use_container_width=True)

    if submitted:
        with st.spinner("Téléchargement OSM et calculs…"):
            st.session_state.result = analysis.run(
                city=city, mode=mode, radius_km=radius_km,
                do_centrality=do_centrality, do_closeness=do_closeness, do_degree=do_degree,
                do_h3=do_h3, h3_res=h3_res, color_by=color_by
            )

    result = st.session_state.result
    if not result:
        st.info("Configurez et lancez l’analyse.")
        return

    if result.get("error"):
        st.error(result["error"])
        if result.get("trace"):
            with st.expander("Trace"):
                st.code(result["trace"])
        return

    st.success("Analyse terminée ✅")

    m = result["metrics"]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Nœuds", f"{m.get('nodes',0):,}".replace(","," "))
    k2.metric("Arêtes", f"{m.get('edges',0):,}".replace(","," "))
    k3.metric("Longueur (km)", f"{m.get('total_km',0):.2f}")
    k4.metric("Composantes", f"{m.get('components',0)}")

    fmap = map_mod.build_map(result, color_by=result.get("color_by","length"))
    st_folium(fmap, height=640, use_container_width=True)

    if "metrics_df" in result and not result["metrics_df"].empty:
        st.subheader("Indicateurs détaillés")
        st.dataframe(result["metrics_df"], use_container_width=True)

    st.subheader("Téléchargements")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("GeoJSON — réseau", result["edges_geojson"].encode("utf-8"),
                        file_name="reseau.geojson", mime="application/geo+json", use_container_width=True)
    with d2:
        st.download_button("CSV — indicateurs", result["metrics_csv"].encode("utf-8"),
                        file_name="indicateurs.csv", mime="text/csv", use_container_width=True)
    with d3:
        if result.get("h3_geojson"):
            st.download_button("GeoJSON — H3", result["h3_geojson"].encode("utf-8"),
                            file_name="h3.geojson", mime="application/geo+json", use_container_width=True)

    if st.button("↩ Rejouer", type="secondary"):
        st.session_state.result = None
        st.experimental_rerun()
