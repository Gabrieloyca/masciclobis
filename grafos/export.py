# grafos/export.py — versión sin PDF para Streamlit Cloud
from __future__ import annotations
from typing import Dict, Optional
import geopandas as gpd

def export_geojson(gdf: gpd.GeoDataFrame, path: str) -> str:
    gdf.to_file(path, driver="GeoJSON")
    return path

def export_csv(df, path: str) -> str:
    df.to_csv(path, index=False)
    return path

def export_pdf(_: Dict, __: Optional[str] = None) -> Optional[str]:
    # PDF desactivado en despliegue cloud para evitar dependencias del sistema (Pango/Cairo).
    return None
