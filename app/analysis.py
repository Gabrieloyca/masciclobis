
from __future__ import annotations
import traceback
import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx as ox

from grafos import loader, prepare, metrics

import streamlit as st

@st.cache_data(show_spinner=False)
def _compute(city: str, mode: str, radius_km: float, do_centrality: bool, do_h3: bool, h3_res: int):
    G = loader.load_city_graph(city, mode=mode, distance=int(radius_km*1000))
    G = prepare.prepare_graph(G)

    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True, fill_edge_geometry=True)

    m = metrics.compute_metrics(G)
    if do_centrality:
        edges = metrics.add_edge_betweenness(G, edges)

    h3_gdf = None
    if do_h3:
        h3_gdf = metrics.aggregate_h3(edges, res=h3_res)

    edges_geojson = edges.to_crs(4326).to_json(drop_id=True)
    metrics_df = pd.DataFrame([m]).T.reset_index()
    metrics_df.columns = ["indicateur", "valeur"]
    metrics_csv = metrics_df.to_csv(index=False)

    h3_geojson = h3_gdf.to_crs(4326).to_json(drop_id=True) if h3_gdf is not None else None

    return {
        "edges_geojson": edges_geojson,
        "metrics_csv": metrics_csv,
        "nodes": nodes,
        "edges": edges,
        "metrics": m,
        "metrics_df": metrics_df,
        "h3_gdf": h3_gdf,
        "h3_geojson": h3_geojson,
    }

def run(city: str, mode: str, radius_km: float, do_centrality: bool, do_h3: bool, h3_res: int):
    try:
        return _compute(city, mode, radius_km, do_centrality, do_h3, h3_res)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()}
