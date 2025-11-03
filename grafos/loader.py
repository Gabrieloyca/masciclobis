from __future__ import annotations
from typing import Iterable, Literal, Optional

import math
import os
from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import osmnx as ox
from shapely.geometry import LineString


__all__ = [
    "OpenStreetMapUnavailable",
    "configure_osmnx",
    "load_city_graph",
    "synthetic_graph",
    "get_graph",
]


DEFAULT_OVERPASS_ENDPOINTS: tuple[str, ...] = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/cgi/interpreter",
)


@dataclass
class OpenStreetMapUnavailable(RuntimeError):
    """Error raised when OSM data cannot be downloaded."""

    city: str
    mode: str
    distance: int
    endpoints: tuple[str, ...]
    errors: tuple[str, ...]

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        attempted = ", ".join(self.endpoints) or "(no endpoints configured)"
        details = "; ".join(self.errors) or "unknown error"
        return (
            f"No se pudo descargar la red de {self.city!r} ({self.mode}) a {self.distance} m "
            f"desde Overpass. Endpoints intentados: {attempted}. Últimos errores: {details}."
        )


def _iter_endpoints() -> Iterable[str]:
    configured = os.environ.get("OVERPASS_API_URL")
    if configured:
        yield configured.strip()
    extra = os.environ.get("OVERPASS_EXTRA_ENDPOINTS")
    if extra:
        for endpoint in extra.split(","):
            endpoint = endpoint.strip()
            if endpoint:
                yield endpoint
    for endpoint in DEFAULT_OVERPASS_ENDPOINTS:
        yield endpoint


def _ensure_cache_dir() -> Optional[Path]:
    cache_dir = os.environ.get("OSM_CACHE_DIR")
    if not cache_dir:
        return None
    path = Path(cache_dir).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_osmnx() -> None:
    """Configure global osmnx settings respecting environment overrides."""

    ox.settings.use_cache = True
    ox.settings.overpass_rate_limit = True
    ox.settings.timeout = int(os.environ.get("OVERPASS_TIMEOUT", 180))
    ox.settings.log_console = False

    cache_dir = _ensure_cache_dir()
    if cache_dir is not None:
        ox.settings.cache_folder = str(cache_dir)

    # Merge proxy configuration if provided
    proxies = {}
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if http_proxy:
        proxies["http"] = http_proxy
    if https_proxy:
        proxies["https"] = https_proxy
    if proxies:
        req_kwargs = dict(ox.settings.requests_kwargs or {})
        req_kwargs["proxies"] = proxies
        ox.settings.requests_kwargs = req_kwargs


configure_osmnx()


def load_city_graph(
    city: str,
    mode: Literal["walk", "bike", "drive"] = "walk",
    distance: int = 2000,
) -> nx.MultiDiGraph:
    """Download a graph for ``city`` from Overpass.

    The function iterates through a list of endpoints (user supplied or defaults)
    and returns as soon as one request succeeds. If all endpoints fail an
    :class:`OpenStreetMapUnavailable` error is raised with aggregated context.
    """

    local_graph = os.environ.get("OSM_GRAPHML_PATH")
    if local_graph:
        path = Path(local_graph).expanduser()
        if path.exists():
            return ox.load_graphml(filepath=str(path))

    endpoints = list(_iter_endpoints())

    try:
        lat, lon = ox.geocode(city)
    except Exception as exc:  # pragma: no cover - network failure
        raise OpenStreetMapUnavailable(
            city=city,
            mode=mode,
            distance=distance,
            endpoints=tuple(endpoints),
            errors=(f"geocode: {exc}",),
        ) from exc

    network_type = mode if mode in {"walk", "bike", "drive"} else "walk"

    errors: list[str] = []
    attempted: list[str] = []
    for endpoint in endpoints:
        if not endpoint:
            continue
        attempted.append(endpoint)
        ox.settings.overpass_endpoint = endpoint
        try:
            return ox.graph_from_point(
                (lat, lon),
                dist=distance,
                network_type=network_type,
                simplify=True,
            )
        except Exception as exc:  # pragma: no cover - network errors vary
            errors.append(f"{endpoint}: {exc}")
            continue

    raise OpenStreetMapUnavailable(
        city=city,
        mode=network_type,
        distance=distance,
        endpoints=tuple(attempted),
        errors=tuple(errors),
    )

def synthetic_graph(
    center=(43.7384, 7.4246),
    size_m: int = 800,
    step_m: int = 100,
) -> nx.MultiDiGraph:
    deg_lat = step_m / 111320.0
    deg_lon = step_m / (111320.0 * math.cos(math.radians(center[0])))
    graph = nx.MultiDiGraph()
    n = int(size_m / step_m)

    def _node_id(i: int, j: int) -> str:
        return f"{i}_{j}"

    for i in range(-n // 2, n // 2 + 1):
        for j in range(-n // 2, n // 2 + 1):
            lat = center[0] + i * deg_lat
            lon = center[1] + j * deg_lon
            graph.add_node(_node_id(i, j), y=lat, x=lon)

    def _edge(u, v):
        return LineString(
            [
                (graph.nodes[u]["x"], graph.nodes[u]["y"]),
                (graph.nodes[v]["x"], graph.nodes[v]["y"]),
            ]
        )

    for i in range(-n // 2, n // 2 + 1):
        for j in range(-n // 2, n // 2):
            u = _node_id(i, j)
            v = _node_id(i, j + 1)
            graph.add_edge(u, v, length=step_m, geometry=_edge(u, v))
            graph.add_edge(v, u, length=step_m, geometry=_edge(v, u))

    for i in range(-n // 2, n // 2):
        for j in range(-n // 2, n // 2 + 1):
            u = _node_id(i, j)
            v = _node_id(i + 1, j)
            graph.add_edge(u, v, length=step_m, geometry=_edge(u, v))
            graph.add_edge(v, u, length=step_m, geometry=_edge(v, u))

    graph.graph["crs"] = "EPSG:4326"
    return graph


def get_graph(
    city: str,
    mode: Literal["walk", "bike", "drive"] = "walk",
    distance: int = 2000,
    fallback_to_synthetic: bool | None = None,
) -> nx.MultiDiGraph:
    """Download a graph, optionally falling back to a synthetic sample."""

    try:
        return load_city_graph(city, mode, distance)
    except OpenStreetMapUnavailable:
        allow = (
            fallback_to_synthetic
            if fallback_to_synthetic is not None
            else os.environ.get("ALLOW_SYNTHETIC_GRAPH", "0") == "1"
        )
        if allow:
            return synthetic_graph()
        raise
