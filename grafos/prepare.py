
from __future__ import annotations
import osmnx as ox
import networkx as nx

def prepare_graph(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    try:
        return ox.project_graph(G)
    except Exception:
        return G
