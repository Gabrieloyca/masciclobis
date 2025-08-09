from __future__ import annotations
from typing import Literal
import osmnx as ox
import networkx as nx
import math
from shapely.geometry import LineString

# Ajustes para Overpass y tiempos de espera razonables en cloud
ox.settings.overpass_rate_limit = True
ox.settings.timeout = 180
ox.settings.use_cache = True
ox.settings.log_console = False

def load_city_graph(city: str, mode: Literal["walk","bike"]="walk", distance: int = 2000) -> nx.MultiDiGraph:
    lat, lon = ox.geocode(city)
    network_type = "walk" if mode=="walk" else "bike"
    G = ox.graph_from_point((lat, lon), dist=distance, network_type=network_type, simplify=True)
    return G

def synthetic_graph(center=(43.7384, 7.4246), size_m: int = 800, step_m: int = 100) -> nx.MultiDiGraph:
    deg_lat = step_m / 111320.0
    deg_lon = step_m / (111320.0 * math.cos(math.radians(center[0])))
    G = nx.MultiDiGraph()
    n = int(size_m/step_m)
    for i in range(-n//2, n//2+1):
        for j in range(-n//2, n//2+1):
            lat = center[0] + i*deg_lat
            lon = center[1] + j*deg_lon
            G.add_node((i,j), y=lat, x=lon)
    for i in range(-n//2, n//2+1):
        for j in range(-n//2, n//2):
            u = (i,j); v = (i,j+1)
            G.add_edge(u,v, length=step_m, geometry=LineString([(G.nodes[u]['x'],G.nodes[u]['y']),(G.nodes[v]['x'],G.nodes[v]['y'])]))
            G.add_edge(v,u, length=step_m, geometry=LineString([(G.nodes[v]['x'],G.nodes[v]['y']),(G.nodes[u]['x'],G.nodes[u]['y'])]))
    for i in range(-n//2, n//2):
        for j in range(-n//2, n//2+1):
            u = (i,j); v = (i+1,j)
            G.add_edge(u,v, length=step_m, geometry=LineString([(G.nodes[u]['x'],G.nodes[u]['y']),(G.nodes[v]['x'],G.nodes[v]['y'])]))
            G.add_edge(v,u, length=step_m, geometry=LineString([(G.nodes[v]['x'],G.nodes[v]['y']),(G.nodes[u]['x'],G.nodes[u]['y'])]))
    return G

def get_graph(city: str, mode: Literal["walk","bike"]="walk", distance: int = 2000) -> nx.MultiDiGraph:
    try:
        return load_city_graph(city, mode, distance)
    except Exception:
        return synthetic_graph()
