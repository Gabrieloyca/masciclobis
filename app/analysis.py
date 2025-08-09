
from __future__ import annotations
import traceback
import pandas as pd
import geopandas as gpd
import osmnx as ox
from grafos import loader, prepare, metrics
import streamlit as st

@st.cache_data(show_spinner=False)
def _compute(city: str, mode: str, radius_km: float,
             do_centrality: bool, do_closeness: bool, do_degree: bool,
             do_h3: bool, h3_res: int, color_by: str):
    G = loader.get_graph(city, mode=mode, distance=int(radius_km*1000))
    G = prepare.prepare_graph(G)
    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True, fill_edge_geometry=True)

    m = metrics.compute_metrics(G)
    if do_centrality:
        edges = metrics.add_edge_betweenness(G, edges)

    if do_closeness or do_degree:
        nodes_metrics = metrics.node_centralities(G, closeness=do_closeness, degree=do_degree)
        edges = metrics.attach_node_metrics_to_edges(edges, nodes_metrics)

    h3_gdf = metrics.aggregate_h3(edges, res=h3_res) if do_h3 else None

    edges_geojson = edges.to_crs(4326).to_json(drop_id=True)
    metrics_df = pd.DataFrame([m]).T.reset_index()
    metrics_df.columns = ["indicateur", "valeur"]
    metrics_csv = metrics_df.to_csv(index=False)
    h3_geojson = h3_gdf.to_crs(4326).to_json(drop_id=True) if h3_gdf is not None and not h3_gdf.empty else None

    return {
        "nodes": nodes, "edges": edges,
        "metrics": m, "metrics_df": metrics_df,
        "edges_geojson": edges_geojson, "metrics_csv": metrics_csv,
        "h3_gdf": h3_gdf, "h3_geojson": h3_geojson,
        "color_by": color_by,
    }

def run(**kwargs):
    try:
        return _compute(**kwargs)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()}
