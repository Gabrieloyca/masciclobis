"""Tests for the data loader module."""

import pytest

from grafos import loader


def test_synthetic_graph_shape():
    graph = loader.synthetic_graph()
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0


@pytest.mark.network
def test_load_city_graph_smoke():
    """Ensure that a graph can be downloaded for a known small city."""
    try:
        G = loader.load_city_graph("Monaco, Monaco", mode="walk", distance=500)
    except loader.OpenStreetMapUnavailable as exc:
        pytest.skip(f"Overpass API unavailable: {exc}")

    assert G.number_of_nodes() > 0
    assert G.number_of_edges() > 0


def test_get_graph_allows_synthetic(monkeypatch):
    """When explicit fallback is requested, a synthetic grid is returned."""

    def always_fail(*args, **kwargs):
        raise loader.OpenStreetMapUnavailable("city", "walk", 1000, tuple(), tuple())

    monkeypatch.setattr(loader, "load_city_graph", always_fail)
    G = loader.get_graph("Nowhere", fallback_to_synthetic=True)
    assert G.number_of_nodes() > 0
