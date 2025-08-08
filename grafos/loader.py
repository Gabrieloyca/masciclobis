"""Data loading utilities for the accessibility analysis app.

This module provides functions to download and construct road or
multimodal networks from OpenStreetMap using the osmnx library. It
wraps osmnx helpers and exposes a simple API for retrieving graphs
given a city name and mode of transport.
"""

from __future__ import annotations

from typing import Literal, Tuple

import networkx as nx
import osmnx as ox

from app.utils import geocode_city


def load_city_graph(
    city: str,
    mode: Literal["walk", "bike"] = "walk",
    distance: int = 2000,
) -> nx.MultiDiGraph:
    """Download a street network graph around a given city.

    The function geocodes the city name to obtain a coordinate pair and
    then uses osmnx to download the corresponding street network within
    a specified radius. Different network types are selected based on
    the transport mode.

    Parameters
    ----------
    city : str
        Name of the city to analyze.
    mode : {'walk', 'bike'}, optional
        Type of network to download: pedestrian (walk) or cycling (bike).
    distance : int, optional
        Radius around the city centre in metres to include in the graph.

    Returns
    -------
    networkx.MultiDiGraph
        Downloaded street network graph.
    """
    # Determine the appropriate network type for osmnx
    if mode == "walk":
        network_type = "walk"
    elif mode == "bike":
        network_type = "bike"
    else:
        raise ValueError("Mode must be either 'walk' or 'bike'")

    # Geocode the city name to obtain latitude and longitude
    lat, lon = geocode_city(city)
    # Download graph around the point with the given distance
    G = ox.graph_from_point(
        (lat, lon),
        dist=distance,
        network_type=network_type,
        simplify=True,
    )
    # The 'length' attribute is already provided by osmnx on each edge.
    # Additional attributes like bearings, speeds can be added here if needed.
    return G
