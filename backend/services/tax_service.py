from models import OrderInput
from shapely.geometry import Point
import main
import geopandas as gpd
from tax import ny_tax_rates

def calculate_tax(order: OrderInput) -> dict:
    city, county = find(Point(order.longitude, order.latitude))
    tax = get_tax_info(city, county)
    if tax is None:
        main.nevshtati += 1
        return {
            'composite_tax_rate': 8,
            'не_в_штаті': True
        }
    return {
        'composite_tax_rate': tax['total_rate'],
        'tax_amount': order.subtotal*tax['total_rate'],
        'total_amount': order.subtotal + order.subtotal*tax['total_rate'],
        'jurisdictions': tax['code'],
        'breakdown': {
            'state_rate': 0.04,
            'county_rate': tax['county_rate'],
            'special_rate': tax['special_rate']
        }
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
        return {"county_rate": 0, "city_rate": 0, "special_rate": 0, "total_rate": 0, "code": None}

    city_clean = str(city_name).strip().lower()
    county_clean = str(county_name).strip().lower()

    # Обробка Нью-Йорка
    nyc_boroughs = ["bronx", "kings", "new york", "queens", "richmond"]
    if county_clean in nyc_boroughs:
        city_clean = "new york city"

    # Ініціалізація результатів
    tax_info = {
        "county_rate": 0.0,
        "city_rate": 0.0,
        "special_rate": 0.0,
        "code": None
    }

    # 1. Пошук податку округу
    for entry in ny_tax_rates:
        if not entry.get("is_city") and county_clean == entry["clean_name"].lower():
            tax_info["county_rate"] = entry.get("rate", 0.0)
            tax_info["code"] = entry.get("code")  # Зазвичай код прив'язаний до округу/міста
            break

    # 2. Пошук податку міста (якщо він є окремо)
    for entry in ny_tax_rates:
        if entry.get("is_city") and city_clean == entry["clean_name"].lower():
            tax_info["city_rate"] = entry.get("rate", 0.0)
            # Якщо код міста пріоритетніший, оновлюємо його
            if entry.get("code"):
                tax_info["code"] = entry["code"]
            break

    # 3. Пошук спеціального податку (наприклад, MCTD - Metropolitan Commuter Transportation District)
    # Припускаємо, що у вашому списку є записи з типом "special" або за певною назвою
    for entry in ny_tax_rates:
        if entry.get("type") == "special" and county_clean in entry.get("applicable_counties", []):
            tax_info["special_rate"] = entry.get("rate", 0.0)
            break

    # Розрахунок загальної ставки
    tax_info["total_rate"] = tax_info["county_rate"] + tax_info["city_rate"] + tax_info["special_rate"]

    return tax_info