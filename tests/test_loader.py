"""Tests for the data loader module."""

from grafos import loader


def test_load_city_graph_smoke():
    """Ensure that a graph can be downloaded for a known small city."""
    G = loader.load_city_graph("Monaco, Monaco", mode="walk", distance=500)
    # Basic assertions on graph properties
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0
