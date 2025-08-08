"""Tests for the metrics computation module."""

from grafos import loader, metrics


def test_compute_metrics_keys():
    """Verify that the compute_metrics function returns expected keys."""
    G = loader.load_city_graph("Monaco, Monaco", mode="walk", distance=300)
    results = metrics.compute_metrics(G)
    assert "Nombre de nœuds" in results
    assert "Nombre d'arêtes" in results
    assert "Longueur totale (km)" in results
    # Values should be non-negative
    for value in results.values():
        assert value >= 0
