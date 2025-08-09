
from __future__ import annotations
import osmnx as ox
import networkx as nx

def prepare_graph(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    try:
        Gp = ox.project_graph(G)
        return Gp
    except Exception:
        return G
