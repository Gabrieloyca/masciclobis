"""Tests for the metrics computation module."""

import osmnx as ox

from grafos import loader, metrics


def _sample_edges():
    G = loader.synthetic_graph()
    nodes, edges = ox.graph_to_gdfs(
        G, nodes=True, edges=True, fill_edge_geometry=True
    )
    return G, nodes, edges.reset_index()


def test_compute_metrics_keys():
    """Verify that compute_metrics returns core indicators."""
    G, _, _ = _sample_edges()
    results = metrics.compute_metrics(G)
    expected = {
        "nodes",
        "edges",
        "total_km",
        "components",
        "avg_degree",
        "largest_component_nodes",
        "avg_shortest_path_m",
    }
    assert expected.issubset(results.keys())
    assert all(value >= 0 for value in results.values())


def test_node_centralities_columns():
    G, _, _ = _sample_edges()
    df = metrics.node_centralities(
        G,
        closeness=True,
        degree=True,
        straightness=True,
        eigenvector=True,
    )
    assert {"node", "degree", "closeness", "straightness", "eigenvector"}.issubset(df.columns)


def test_attach_node_metrics_to_edges():
    G, _, edges = _sample_edges()
    node_df = metrics.node_centralities(
        G,
        closeness=True,
        degree=True,
        straightness=True,
        eigenvector=True,
    )
    enriched = metrics.attach_node_metrics_to_edges(edges, node_df)
    for column in ["degree", "closeness", "straightness", "eigenvector"]:
        assert column in enriched.columns


def test_add_edge_betweenness():
    G, _, edges = _sample_edges()
    enriched = metrics.add_edge_betweenness(G, edges)
    assert "betweenness" in enriched.columns


def test_aggregate_h3_structure():
    _, _, edges = _sample_edges()
    h3_gdf = metrics.aggregate_h3(edges, res=7)
    assert set(["h3", "length_km"]).issubset(h3_gdf.columns)
