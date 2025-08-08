"""Graph preparation utilities.

At present this module does not perform any additional processing
beyond what osmnx already does. It is included to provide a place
where future data cleaning, filtering, or augmentation logic can live.
"""

from __future__ import annotations

import networkx as nx


def prepare_graph(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Prepare a street network graph for analysis.

    This function is a placeholder for future processing steps. It
    currently returns the input graph unchanged. In a more advanced
    setting this could be used to filter out certain types of edges,
    simplify turn restrictions, or add custom attributes.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The graph to prepare.

    Returns
    -------
    networkx.MultiDiGraph
        The prepared graph.
    """
    return G
