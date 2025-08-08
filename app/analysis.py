"""Analysis orchestration for the accessibility app.

This module ties together data loading, preparation, metric computation
and export. It exposes functions that can be called from the UI to
perform a complete analysis given a city and user-defined parameters.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import streamlit as st

from grafos import loader, prepare, metrics
from app import utils


@st.cache_data(show_spinner=False)
def run_analysis(
    city: str,
    mode: str,
    radius_m: int,
) -> Tuple[Dict[str, float], object, object]:
    """Run an accessibility analysis for a given city.

    This function orchestrates loading the street network, optionally
    preparing it, computing metrics and converting the graph into a
    GeoDataFrame for display. It uses Streamlit's caching mechanism to
    avoid recomputing results for identical inputs.

    Parameters
    ----------
    city : str
        Name of the city to analyze.
    mode : str
        Mode of travel ('walk' or 'bike').
    radius_m : int
        Radius around the city centre in metres to download the network.

    Returns
    -------
    Tuple[dict, networkx.MultiDiGraph, geopandas.GeoDataFrame]
        A triple containing the computed metrics, the NetworkX graph and
        the GeoDataFrame of edges.
    """
    # Load the graph
    G = loader.load_city_graph(city, mode, radius_m)
    # Prepare (currently a no-op)
    G_prepared = prepare.prepare_graph(G)
    # Compute metrics
    metric_results = metrics.compute_metrics(G_prepared)
    # Convert to GeoDataFrame for mapping
    gdf_edges = utils.graph_to_geodataframe(G_prepared)
    return metric_results, G_prepared, gdf_edges
