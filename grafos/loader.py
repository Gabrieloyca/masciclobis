
from __future__ import annotations
from typing import Literal
import osmnx as ox
import networkx as nx

def load_city_graph(city: str, mode: Literal["walk","bike"]="walk", distance: int = 2000) -> nx.MultiDiGraph:
    if mode not in {"walk","bike"}:
        raise ValueError("mode must be 'walk' or 'bike'")
    lat, lon = ox.geocode(city)
    network_type = "walk" if mode=="walk" else "bike"
    G = ox.graph_from_point((lat, lon), dist=distance, network_type=network_type, simplify=True)
    return G
