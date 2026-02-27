from models import OrderInput
from shapely.geometry import Point
import main
import repository
import geopandas as gpd
from tax import ny_tax_rates

def calculate_tax(order: OrderInput) -> dict:
    city, county = find(Point(order.longitude, order.latitude))
    podatok, code = get_tax_info(city, county)
    if podatok is None:
        main.nevshtati += 1
        return {
            'composite_tax_rate': 8,
            'не_в_штаті': True
        }
    return {
        'composite_tax_rate': float(podatok),
        'tax_amount': order.subtotal*float(podatok),
        'total_amount': order.subtotal + order.subtotal*podatok,
        'jurisdictions': code
    }

def find(point: Point):
    
    point_gdf = gpd.GeoDataFrame(
        geometry=[point],
        crs="EPSG:4326"
    )
    points_projected = point_gdf.to_crs(epsg=3857)

    joined = gpd.sjoin_nearest(points_projected, main.cities, how="left", max_distance=1000)

    return joined.iloc[0]['NAME'], joined.iloc[0]['COUNTY']

def get_tax_info(city_name, county_name):
    if not city_name or not county_name:
        return None, None

    city_clean = str(city_name).strip().lower()
    county_clean = str(county_name).strip().lower()

    # Спеціальна обробка для районів NYC (якщо GeoJSON повернув назву району)
    nyc_boroughs = ["bronx", "kings", "new york", "queens", "richmond"]
    if county_clean in nyc_boroughs:
        city_clean = "new york city"

    # 1. Шукаємо спочатку в містах (пріоритет винятків)
    for entry in ny_tax_rates:
        if entry["is_city"] and city_clean == entry["clean_name"].lower():
            return entry["rate"], entry["code"]
    
    # 2. Якщо міста не знайдено, шукаємо по округу
    for entry in ny_tax_rates:
        if not entry["is_city"] and county_clean == entry["clean_name"].lower():
            return entry["rate"], entry["code"]
            
    return None, None