"""Export utilities for the accessibility analysis app.

This module defines functions to write analysis outputs to various
formats, including GeoJSON, CSV and PDF. It relies on geopandas for
spatial exports and weasyprint to convert simple HTML summaries into
PDF documents.
"""

from __future__ import annotations

import io
import os
import tempfile
from typing import Dict, Optional, Tuple

import geopandas as gpd
from weasyprint import HTML, CSS


def export_geojson(gdf: gpd.GeoDataFrame, filepath: str) -> None:
    """Export a GeoDataFrame to a GeoJSON file.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        The GeoDataFrame to export. Must have geometry column set.
    filepath : str
        Path where the GeoJSON file will be saved.
    """
    gdf.to_file(filepath, driver="GeoJSON")


def export_csv(gdf: gpd.GeoDataFrame, filepath: str) -> None:
    """Export a GeoDataFrame to a CSV file (non-spatial attributes only).

    The geometry column is dropped since CSV does not support spatial
    types. Use GeoJSON or Parquet for spatial exports.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        The GeoDataFrame to export.
    filepath : str
        Path where the CSV file will be saved.
    """
    df = gdf.drop(columns=["geometry"])
    df.to_csv(filepath, index=False)


def export_pdf(
    metrics: Dict[str, float],
    city: str,
    filepath: str,
    *,
    map_path: Optional[str] = None,
) -> None:
    """Export analysis summary to a PDF report.

    A simple HTML template is constructed on the fly using the provided
    metrics and optionally an embedded map image. WeasyPrint is used
    to convert the HTML into a PDF file. If a map image path is
    provided, it will be included at the top of the report.

    Parameters
    ----------
    metrics : dict
        Dictionary of metric names to values.
    city : str
        Name of the city analysed, displayed in the report header.
    filepath : str
        Path where the PDF file will be saved.
    map_path : str, optional
        Optional path to a PNG image of the map to include.
    """
    # Compose a simple HTML report
    rows = "".join(
        f"<tr><td style='padding:4px'>{key}</td><td style='padding:4px;text-align:right'>{value}</td></tr>"
        for key, value in metrics.items()
    )
    import base64  # imported here to avoid unused import if not used

    map_html = ""
    if map_path and os.path.exists(map_path):
        # Embed the image using a base64 data URI
        with open(map_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        data_uri = f"data:image/png;base64,{encoded}"
        map_html = (
            f"<img src='{data_uri}' alt='Carte' style='width:100%;height:auto;margin-bottom:10px;'>"
        )
    html = f"""
    <html>
    <head>
      <meta charset='UTF-8'>
      <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
      </style>
    </head>
    <body>
      <h1>Rapport d'accessibilité – {city}</h1>
      {map_html}
      <table>
        <tr><th>Métrique</th><th>Valeur</th></tr>
        {rows}
      </table>
    </body>
    </html>
    """
    # Write the PDF
    HTML(string=html).write_pdf(filepath)
