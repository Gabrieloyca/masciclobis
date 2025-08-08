import geopandas as gpd
import pandas as pd

def run(city, mode, radius):
    # Simulation de traitement
    data = {
        'lat': [48.8566, 48.8666],
        'lon': [2.3522, 2.3622],
        'valeur': [1, 2]
    }
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['lon'], data['lat']), crs="EPSG:4326")
    table = pd.DataFrame({'indicateur': ['Accessibilité'], 'valeur': [42]})
    return gdf, table