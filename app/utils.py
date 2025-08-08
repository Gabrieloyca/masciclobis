"""Utility functions for the accessibility analysis app.

This module contains helper functions used throughout the application.
It primarily deals with geocoding city names to coordinates, converting
graphs to GeoDataFrames for display, and formatting metrics for output.
"""

from __future__ import annotations

import functools
import logging
from typing import Tuple

import geopandas as gpd
import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim
from shapely.geometry import LineString, Point

logger = logging.getLogger(__name__)


@functools.lru_cache(maxsize=64)
def geocode_city(city: str) -> Tuple[float, float]:
    """Geocode a city name to latitude and longitude.

    This function uses geopy's Nominatim geocoder to convert a human‐
    readable place name into geographic coordinates. The results are
    cached to avoid redundant network calls during repeated analyses.

    Parameters
    ----------
    city: str
        Name of the city to geocode. Should include country if ambiguous.

    Returns
    -------
    Tuple[float, float]
        A tuple of (latitude, longitude).
    """
    geolocator = Nominatim(user_agent="grafos-accesibilidad-app")
    location = geolocator.geocode(city)
    if location is None:
        raise ValueError(f"Could not geocode city: {city}")
    return (location.latitude, location.longitude)


def graph_to_geodataframe(G: nx.MultiDiGraph) -> gpd.GeoDataFrame:
    """Convert a NetworkX graph to a GeoDataFrame of edges.

    Each edge in the graph is represented as a row with a LineString
    geometry. The function drops duplicate geometries and resets the
    index to provide a clean table for display and export.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The graph to convert. Must contain 'geometry' attribute on edges
        for accurate spatial representation.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with one row per unique edge geometry.
    """
    # Convert to GeoDataFrame using osmnx helper
    gdf_edges = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
    # Ensure unique geometries and reset index for clarity
    gdf_edges = gdf_edges.drop_duplicates(subset=["geometry"]).reset_index(drop=True)
    return gdf_edges


def summary_metrics(G: nx.MultiDiGraph) -> dict[str, float]:
    """Compute simple summary metrics from a graph.

    Currently this returns the number of nodes, number of edges and
    total length of the network in kilometres. Additional metrics can
    easily be added here in the future.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        Graph from which to compute metrics. Assumes 'length' attribute
        on edges in metres.

    Returns
    -------
    dict[str, float]
        Dictionary with keys 'nodes', 'edges' and 'length_km'.
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    # Sum all edge lengths; edges may have multiple parallel edges
    total_length_m = sum(data.get("length", 0) for u, v, key, data in G.edges(keys=True, data=True))
    total_length_km = total_length_m / 1000.0
    return {
        "Nombre de nœuds": float(n_nodes),
        "Nombre d'arêtes": float(n_edges),
        "Longueur totale (km)": float(round(total_length_km, 2)),
    }
