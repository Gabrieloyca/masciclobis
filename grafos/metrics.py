from __future__ import annotations
from typing import Dict

import math

import geopandas as gpd
import h3
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Polygon

def compute_metrics(G: nx.MultiDiGraph) -> Dict[str, float]:
    nodes = G.number_of_nodes()
    edges = G.number_of_edges()
    try:
        ge = ox.graph_to_gdfs(G, nodes=False, edges=True, fill_edge_geometry=True)
        total_km = float(ge.get("length", pd.Series(0)).sum() / 1000.0)
    except Exception:
        total_km = 0.0

    Gu = G.to_undirected()
    comps = nx.number_connected_components(Gu)
    component_sizes = sorted((len(c) for c in nx.connected_components(Gu)), reverse=True)
    giant_size = component_sizes[0] if component_sizes else 0

    avg_deg = sum(dict(G.degree()).values()) / nodes if nodes else 0.0

    try:
        avg_path_length = nx.average_shortest_path_length(Gu, weight="length")
    except Exception:
        avg_path_length = 0.0

    return {
        "nodes": nodes,
        "edges": edges,
        "total_km": round(total_km, 3),
        "components": comps,
        "avg_degree": round(avg_deg, 3),
        "largest_component_nodes": giant_size,
        "avg_shortest_path_m": round(float(avg_path_length), 3) if avg_path_length else 0.0,
    }

def add_edge_betweenness(G: nx.MultiDiGraph, edges_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    Gu = G.to_undirected()
    n = Gu.number_of_nodes()
    k = min(300, max(30, n//15))
    bt = nx.betweenness_centrality(Gu, k=k, seed=42, normalized=True)
    def edge_centrality(row):
        u = row.get("u"); v = row.get("v")
        if u in bt and v in bt:
            return (bt[u]+bt[v])/2.0
        return 0.0
    if {"u","v"}.issubset(edges_gdf.columns):
        edges_gdf = edges_gdf.copy()
        edges_gdf["betweenness"] = edges_gdf.apply(edge_centrality, axis=1)
    return edges_gdf

def _straightness_centrality(G: nx.Graph) -> Dict:
    lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight="length"))
    coords = {n: (data.get("x"), data.get("y")) for n, data in G.nodes(data=True)}
    straightness = {}
    for source, targets in lengths.items():
        sx, sy = coords.get(source, (None, None))
        if sx is None or sy is None:
            straightness[source] = 0.0
            continue
        total = 0.0
        count = 0
        for target, network_dist in targets.items():
            if source == target or network_dist <= 0:
                continue
            tx, ty = coords.get(target, (None, None))
            if tx is None or ty is None:
                continue
            euclidean = math.hypot(float(sx) - float(tx), float(sy) - float(ty))
            if euclidean <= 0:
                continue
            ratio = euclidean / network_dist
            if math.isfinite(ratio):
                total += ratio
                count += 1
        straightness[source] = total / count if count else 0.0
    return straightness


def node_centralities(
    G: nx.MultiDiGraph,
    closeness: bool = True,
    degree: bool = True,
    straightness: bool = False,
    eigenvector: bool = False,
) -> pd.DataFrame:
    Gu = G.to_undirected()
    out = pd.DataFrame({"node": list(Gu.nodes())})
    out.set_index("node", inplace=True)
    if degree:
        out["degree"] = pd.Series(dict(Gu.degree()))
    if closeness:
        out["closeness"] = pd.Series(nx.closeness_centrality(Gu, wf_improved=True))
    if straightness:
        try:
            out["straightness"] = pd.Series(_straightness_centrality(Gu))
        except Exception:
            out["straightness"] = 0.0
    if eigenvector:
        try:
            out["eigenvector"] = pd.Series(
                nx.eigenvector_centrality_numpy(Gu, weight="length")
            )
        except Exception:
            out["eigenvector"] = 0.0
    return out.reset_index()

def attach_node_metrics_to_edges(edges_gdf: gpd.GeoDataFrame, nodes_df: pd.DataFrame) -> gpd.GeoDataFrame:
    g = edges_gdf.copy()
    if not {"u","v"}.issubset(g.columns):
        return g
    for col in [c for c in ["degree", "closeness", "straightness", "eigenvector"] if c in nodes_df.columns]:
        g = g.merge(nodes_df[["node", col]].rename(columns={"node":"u", col: f"{col}_u"}), on="u", how="left")
        g = g.merge(nodes_df[["node", col]].rename(columns={"node":"v", col: f"{col}_v"}), on="v", how="left")
        g[col] = g[[f"{col}_u", f"{col}_v"]].mean(axis=1)
        g.drop(columns=[f"{col}_u", f"{col}_v"], inplace=True, errors="ignore")
    return g

def aggregate_h3(edges_gdf: gpd.GeoDataFrame, res: int = 7) -> gpd.GeoDataFrame:
    if edges_gdf.empty:
        return gpd.GeoDataFrame(
            columns=["h3", "length_km", "geometry"], geometry="geometry", crs="EPSG:4326"
        )

    g_lonlat = edges_gdf.to_crs(4326)
    g_proj = edges_gdf.to_crs(3857)
    centers_proj = g_proj.geometry.interpolate(0.5, normalized=True)
    centers = gpd.GeoSeries(centers_proj, crs=g_proj.crs).to_crs(4326)

    hexes = [h3.geo_to_h3(lat, lon, res) for lat, lon in zip(centers.y, centers.x)]
    lengths = g_lonlat.get("length", 0).fillna(0).values
    df = pd.DataFrame({"h3": hexes, "length_m": lengths})
    agg = df.groupby("h3", as_index=False)["length_m"].sum()
    polys = [Polygon(h3.h3_to_geo_boundary(h, geo_json=True)) for h in agg["h3"]]
    out = gpd.GeoDataFrame(agg, geometry=polys, crs="EPSG:4326")
    out["length_km"] = out["length_m"] / 1000.0
    return out
