"""Map rendering for the accessibility analysis app.

This module encapsulates the creation of interactive maps using
folium, ready to be embedded in Streamlit via the streamlit-folium
package. It defines helpers to build a base map centred on the
analysis area and overlay the street network edges as GeoJSON.
"""

from __future__ import annotations

from typing import Optional

import folium
import geopandas as gpd


def make_map(gdf: gpd.GeoDataFrame) -> folium.Map:
    """Create a folium map from a GeoDataFrame of street edges.

    The map is centred on the mean latitude and longitude of the edge
    geometries. Edges are added as a GeoJson layer with a simple
    styling. A full-screen button is provided for better usability.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame containing line geometries of the street network.

    Returns
    -------
    folium.Map
        A folium map object ready for display in Streamlit.
    """
    # Compute centroid of all geometries for map centering
    if gdf.empty:
        # Default to 0,0 if no geometries
        centre = (0, 0)
    else:
        centre_geom = gdf.unary_union.centroid
        centre = (centre_geom.y, centre_geom.x)

    m = folium.Map(location=centre, zoom_start=13, control_scale=True)
    # Add network edges as a GeoJson layer
    folium.GeoJson(
        gdf,
        name="Réseau",
        style_function=lambda x: {
            "color": "#0074D9",
            "weight": 2,
        },
        tooltip=folium.GeoJsonTooltip(fields=[], aliases=[]),
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)
    return m
