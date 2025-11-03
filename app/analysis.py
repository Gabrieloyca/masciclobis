from __future__ import annotations

import traceback
from typing import Any, Dict

import pandas as pd


def _compute(
    city: str,
    mode: str,
    radius_km: float,
    do_centrality: bool,
    do_closeness: bool,
    do_degree: bool,
    do_straightness: bool = False,
    do_eigenvector: bool = False,
    do_h3: bool = True,
    h3_res: int = 7,
    color_by: str = "length",
    allow_synthetic: bool = False,
) -> Dict[str, Any]:
    """Execute the analysis workflow and return intermediate objects."""

    # Imports lourds gardés ici pour limiter le temps de chargement initial
    import osmnx as ox
    from grafos import loader, metrics, prepare

    G = loader.get_graph(
        city,
        mode=mode,
        distance=int(radius_km * 1000),
        fallback_to_synthetic=allow_synthetic,
    )
    G = prepare.prepare_graph(G)

    nodes, edges = ox.graph_to_gdfs(G, nodes=True, edges=True, fill_edge_geometry=True)

    summary_metrics = metrics.compute_metrics(G)
    if do_centrality:
        edges = metrics.add_edge_betweenness(G, edges)

    if any([do_closeness, do_degree, do_straightness, do_eigenvector]):
        node_metrics = metrics.node_centralities(
            G,
            closeness=do_closeness,
            degree=do_degree,
            straightness=do_straightness,
            eigenvector=do_eigenvector,
        )
        edges = metrics.attach_node_metrics_to_edges(edges, node_metrics)

    h3_gdf = metrics.aggregate_h3(edges, res=h3_res) if do_h3 else None

    for col in ["betweenness", "closeness", "degree", "straightness", "eigenvector"]:
        if col in edges.columns:
            series = edges[col].fillna(0)
            summary_metrics[f"{col}_mean"] = float(series.mean())
            summary_metrics[f"{col}_max"] = float(series.max())

    edges_geojson = edges.to_crs(4326).to_json(drop_id=True)
    metrics_df = pd.DataFrame([summary_metrics]).T.reset_index()
    metrics_df.columns = ["indicateur", "valeur"]
    metrics_csv = metrics_df.to_csv(index=False)
    h3_geojson = (
        h3_gdf.to_crs(4326).to_json(drop_id=True)
        if h3_gdf is not None and not h3_gdf.empty
        else None
    )

    return {
        "nodes": nodes,
        "edges": edges,
        "metrics": summary_metrics,
        "metrics_df": metrics_df,
        "edges_geojson": edges_geojson,
        "metrics_csv": metrics_csv,
        "h3_gdf": h3_gdf,
        "h3_geojson": h3_geojson,
        "color_by": color_by,
    }


def run(**kwargs) -> Dict[str, Any]:
    try:
        return _compute(**kwargs)
    except Exception as exc:  # pragma: no cover - ensures trace returned to UI
        try:
            from grafos.loader import OpenStreetMapUnavailable

            if isinstance(exc, OpenStreetMapUnavailable):
                return {
                    "error": str(exc),
                    "code": "osm_unavailable",
                    "endpoints": list(exc.endpoints),
                }
        except Exception:
            pass
        return {"error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()}
