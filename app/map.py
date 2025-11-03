from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import branca
import folium
from folium import Choropleth

DEFAULT_COLORS = ["#edf8fb", "#b3cde3", "#8c96c6", "#8856a7", "#810f7c"]


def _legend_html(title: str, items):
    rows = "".join([f"<li><span style='background:{c}'></span>{lab}</li>" for lab, c in items])
    return f"""
    <div style=\"position: fixed; bottom: 20px; left: 20px; z-index:9999; background:white; padding:10px; border:1px solid #ccc;\
    border-radius:8px;\">
      <strong>{title}</strong>
      <ul style=\"list-style:none; padding-left:0; margin:8px 0 0 0;\">
        {rows}
      </ul>
    </div>
    """


def _prepare_scale(series):
    series = series.fillna(0)
    if series.empty or series.max() == series.min():
        return None, [series.mean() if not series.empty else 0]
    qcuts = series.quantile([0.2, 0.4, 0.6, 0.8]).tolist()
    return qcuts, [series.min(), *qcuts, series.max()]


def _color_for(value: float, quantiles: Optional[List[float]]) -> str:
    if not quantiles:
        return "#1976d2"
    if value <= quantiles[0]:
        return DEFAULT_COLORS[0]
    if value <= quantiles[1]:
        return DEFAULT_COLORS[1]
    if value <= quantiles[2]:
        return DEFAULT_COLORS[2]
    if value <= quantiles[3]:
        return DEFAULT_COLORS[3]
    return DEFAULT_COLORS[4]


def build_map(result: dict, color_by: str = "length"):
    """Retained for backward compatibility (folium map generation)."""
    edges = result["edges"].to_crs(4326)
    if edges.empty:
        return folium.Map(location=[48.8566, 2.3522], zoom_start=12)

    center_lat = edges.geometry.centroid.y.mean()
    center_lon = edges.geometry.centroid.x.mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, control_scale=True)

    var = color_by if color_by in edges.columns else "length"
    series = edges[var].fillna(0)
    quantiles, _ = _prepare_scale(series)

    folium.GeoJson(
        edges.to_json(),
        name=f"Réseau ({var})",
        style_function=lambda f: {
            "color": _color_for(f["properties"].get(var, 0), quantiles),
            "weight": 2,
            "opacity": 0.9,
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=[c for c in ["name", "highway", "length", "betweenness", "closeness", "degree"] if c in edges.columns],
            aliases=["Nom", "Type", "Longueur (m)", "Betweenness", "Closeness", "Degré"],
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
            ("Très faible", DEFAULT_COLORS[0]),
            ("Faible", DEFAULT_COLORS[1]),
            ("Moyenne", DEFAULT_COLORS[2]),
            ("Élevée", DEFAULT_COLORS[3]),
            ("Très élevée", DEFAULT_COLORS[4]),
        ]
        legend = branca.element.MacroElement()
        legend._template = branca.element.Template(_legend_html(f"Échelle — {var}", legend_items))
        m.get_root().add_child(legend)

    return m


def build_map_payload(result: Dict[str, Any], color_by: str = "length") -> Dict[str, Any]:
    edges = result["edges"].to_crs(4326)
    if edges.empty:
        return {
            "center": {"lat": 48.8566, "lng": 2.3522},
            "zoom": 12,
            "colorBy": color_by,
            "quantiles": [],
            "palette": DEFAULT_COLORS,
            "legend": [
                {"label": "Très faible", "color": DEFAULT_COLORS[0]},
                {"label": "Faible", "color": DEFAULT_COLORS[1]},
                {"label": "Moyenne", "color": DEFAULT_COLORS[2]},
                {"label": "Élevée", "color": DEFAULT_COLORS[3]},
                {"label": "Très élevée", "color": DEFAULT_COLORS[4]},
            ],
            "geojson": {"type": "FeatureCollection", "features": []},
        }

    var = color_by if color_by in edges.columns else "length"
    series = edges[var].fillna(0)
    quantiles, breaks = _prepare_scale(series)

    geojson = json.loads(edges.to_json())
    for feature in geojson.get("features", []):
        value = feature.get("properties", {}).get(var, 0)
        feature.setdefault("properties", {})["__style"] = {
            "color": _color_for(value, quantiles),
            "weight": 2,
            "opacity": 0.9,
        }

    center_lat = edges.geometry.centroid.y.mean()
    center_lon = edges.geometry.centroid.x.mean()

    legend = [
        {"label": "Très faible", "color": DEFAULT_COLORS[0]},
        {"label": "Faible", "color": DEFAULT_COLORS[1]},
        {"label": "Moyenne", "color": DEFAULT_COLORS[2]},
        {"label": "Élevée", "color": DEFAULT_COLORS[3]},
        {"label": "Très élevée", "color": DEFAULT_COLORS[4]},
    ]

    return {
        "center": {"lat": center_lat, "lng": center_lon},
        "zoom": 13,
        "colorBy": var,
        "quantiles": quantiles or [],
        "palette": DEFAULT_COLORS,
        "legend": legend,
        "breaks": breaks,
        "geojson": geojson,
    }


def h3_payload(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    h3_gdf = result.get("h3_gdf")
    if h3_gdf is None or h3_gdf.empty:
        return None

    geojson = json.loads(h3_gdf.to_crs(4326).to_json())
    return {
        "geojson": geojson,
        "properties": ["h3", "length_km"],
    }
