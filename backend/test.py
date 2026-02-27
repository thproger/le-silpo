import geopandas as gpd
from shapely.geometry import Point, Polygon
from tax import ny_tax_rates

with open('Cities_Towns.geojson', 'r') as file:
    cities = gpd.read_file(file)

point = Point(-78.8671866447861,42.01246326237433)


def find(point: Point):
    point_gdf = gpd.GeoDataFrame(
        geometry=[point],
        crs="EPSG:4326"
    )

    joined = gpd.sjoin(point_gdf, cities, how="left", predicate="intersects")

    return joined.iloc[0]['NAME'], joined.iloc[0]['COUNTY']

def get_tax_info(city_name, county_name):
    if not city_name or not county_name:
        return None, None

    city_clean = str(city_name).strip().lower()
    county_clean = str(county_name).strip().lower()

    nyc_boroughs = ["bronx", "kings", "new york", "queens", "richmond"]
    if county_clean in nyc_boroughs:
        city_clean = "new york city"

    for entry in ny_tax_rates:
        if entry["is_city"] and city_clean == entry["clean_name"].lower():
            return entry["rate"], entry["code"]
    
    for entry in ny_tax_rates:
        if not entry["is_city"] and county_clean == entry["clean_name"].lower():
            return entry["rate"], entry["code"]
            
    return None, None
