# Export simplifié sans PDF
import geopandas as gpd

def export_geojson(gdf: gpd.GeoDataFrame, path: str) -> str:
    gdf.to_file(path, driver="GeoJSON")
    return path

def export_csv(df, path: str) -> str:
    df.to_csv(path, index=False)
    return path

def export_pdf(*args, **kwargs):
    return None
