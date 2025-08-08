"""Metric computation for the accessibility analysis app.

This module defines functions to compute various graph metrics. At
present only simple summary metrics are implemented, but this is
designed to be easily extensible to include more sophisticated
measures such as centrality, isochrone areas, or access to
amenities.
"""

from __future__ import annotations

from typing import Dict

import networkx as nx

from app.utils import summary_metrics


def compute_metrics(G: nx.MultiDiGraph) -> Dict[str, float]:
    """Compute a set of metrics for the given graph.

    Currently delegates to :func:`summary_metrics` in the utils module
    but can be extended to compute additional indicators like betweenness
    centrality, closeness centrality, network density, etc.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The graph to analyze.

    Returns
    -------
    dict
        Mapping of metric names (in French) to their values.
    """
    return summary_metrics(G)
