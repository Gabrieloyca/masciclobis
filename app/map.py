
from __future__ import annotations
import folium
from folium import Choropleth
import branca

def _legend_html(title: str, items):
    rows = "".join([f"<li><span style='background:{c}'></span>{lab}</li>" for lab, c in items])
    return f"""
    <div style="position: fixed; bottom: 20px; left: 20px; z-index:9999; background:white; padding:10px; border:1px solid #ccc; border-radius:8px;">
      <strong>{title}</strong>
      <ul style="list-style:none; padding-left:0; margin:8px 0 0 0;">
        {rows}
      </ul>
    </div>
    """

def build_map(result: dict, color_by: str = "length"):
    edges = result["edges"].to_crs(4326)
    if edges.empty:
        return folium.Map(location=[48.8566,2.3522], zoom_start=12)

    center_lat = edges.geometry.centroid.y.mean()
    center_lon = edges.geometry.centroid.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, control_scale=True)

    var = color_by if color_by in edges.columns else "length"
    series = edges[var].fillna(0)
    if series.max() == series.min():
        qcuts = None
    else:
        qcuts = series.quantile([0.2,0.4,0.6,0.8]).tolist()

    def color_scale(v):
        if qcuts is None:
            return "#1976d2"
        if v <= qcuts[0]: return "#edf8fb"
        if v <= qcuts[1]: return "#b3cde3"
        if v <= qcuts[2]: return "#8c96c6"
        if v <= qcuts[3]: return "#8856a7"
        return "#810f7c"

    folium.GeoJson(
        edges.to_json(),
        name=f"Réseau ({var})",
        style_function=lambda f: {"color": color_scale(f["properties"].get(var, 0)), "weight": 2, "opacity": 0.9},
        tooltip=folium.features.GeoJsonTooltip(
            fields=[c for c in ["name","highway","length","betweenness","closeness","degree"] if c in edges.columns],
            aliases=["Nom","Type","Longueur (m)","Betweenness","Closeness","Degré"]
        ),
    ).add_to(m)

    h3_gdf = result.get("h3_gdf")
    if h3_gdf is not None and not h3_gdf.empty:
        Choropleth(
            geo_data=h3_gdf.to_json(),
            data=h3_gdf,
            columns=["h3", "length_km"],
            key_on="feature.properties.h3",
            fill_color="YlOrRd",
            fill_opacity=0.6,
            line_opacity=0.2,
            legend_name="Longueur du réseau (km) par hexagone",
            name="H3 (longueur km)",
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    if series.max() != series.min():
        legend_items = [
            ("Très faible", "#edf8fb"),
            ("Faible", "#b3cde3"),
            ("Moyenne", "#8c96c6"),
            ("Élevée", "#8856a7"),
            ("Très élevée", "#810f7c"),
        ]
        legend = branca.element.MacroElement()
        legend._template = branca.element.Template(_legend_html(f"Échelle — {var}", legend_items))
        m.get_root().add_child(legend)

    return m
