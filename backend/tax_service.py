from models import OrderInput, Tax
from shapely.geometry import Point
import main
import geopandas as gpd
import pandas as pd
from tax import ny_tax_rates

def calculate_tax(order: OrderInput) -> Tax:
    city, county = find(Point(order.longitude, order.latitude))
    tax = get_tax_info(city, county)
    return Tax(
        composite_tax_rate=tax['total_rate'],
        tax_amount=order.subtotal+order.subtotal*tax['total_rate'],
        city_rate=tax['city_rate'],
        jurisdictions=tax['code'],
        state_rate=0.04,
        county_rate=tax['county_rate'],
        special_rate=tax['special_rate']
    )

def find(point: Point):
    point_gdf = gpd.GeoDataFrame(
        geometry=[point],
        crs="EPSG:4326"
    )
    if main.usa.crs is not None:
        point_gdf = point_gdf.to_crs(main.usa.crs)
    state_match = gpd.sjoin(point_gdf, main.usa, how="left", predicate="within")

    # Точка поза США
    if state_match.empty or pd.isna(state_match.iloc[0]['name']):
        return None, None
    
    state_name = state_match.iloc[0]['name']
    point_gdf = point_gdf.drop(columns=['index_right'], errors='ignore')
    
    # Визначаємо округ
    county_match = gpd.sjoin(point_gdf, main.counties, how="left", predicate="within")
    county = None
    if not county_match.empty and not pd.isna(county_match.iloc[0]['COUNTY_NAME']):
        county = county_match.iloc[0]['COUNTY_NAME']

    # Довбані 10 точок
    if state_name == "New York" and county is None:
        return None, 'New York'
    elif state_name != 'New York':
        return None, state_name
    
    # Округ уже знайдено
    # 2. Тепер перевіряємо, чи є в цій точці специфічне місто (City)
    point_gdf = point_gdf.drop(columns=['index_right'], errors='ignore')
    city_match = gpd.sjoin(point_gdf, main.cities, how="left", predicate="within")
    
    city = None
    if not city_match.empty and not pd.isna(city_match.iloc[0]['NAME']):
        city = city_match.iloc[0]['NAME']

    return city, county

def find_batch(df: pd.DataFrame):
    """
    Пакетна версія методу find. 
    Приймає DataFrame з колонками 'longitude' та 'latitude'.
    Повертає той самий DataFrame з доданими колонками 'city' та 'county'.
    """
    # 1. Створюємо GeoDataFrame для всіх точок одночасно
    # Переконуємося, що координати — це числа
    lon = pd.to_numeric(df['longitude'], errors='coerce')
    lat = pd.to_numeric(df['latitude'], errors='coerce')
    
    geometry = [Point(xy) for xy in zip(lon, lat)]
    points_gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs="EPSG:4326")
    
    # 2. Приведення до CRS карт (важливо для точності та швидкості)
    if main.usa.crs is not None:
        points_gdf = points_gdf.to_crs(main.usa.crs)

    # 3. Швидкий пошук ШТАТУ (USA)
    # Використовуємо тільки потрібні колонки для економії пам'яті
    points_gdf = gpd.sjoin(points_gdf, main.usa[['name', 'geometry']], how="left", predicate="within")
    points_gdf = points_gdf.rename(columns={'name': 'state_name'}).drop(columns=['index_right'])

    # 4. Швидкий пошук ОКРУГУ (NY Counties)
    points_gdf = gpd.sjoin(points_gdf, main.counties[['COUNTY_NAME', 'geometry']], how="left", predicate="within")
    points_gdf = points_gdf.drop(columns=['index_right'])

    # 5. Швидкий пошук МІСТА (NY Cities)
    points_gdf = gpd.sjoin(points_gdf, main.cities[['NAME', 'geometry']], how="left", predicate="within")
    points_gdf = points_gdf.rename(columns={'NAME': 'city_name', 'COUNTY_NAME': 'county_name'}).drop(columns=['index_right'])

    # 6. Векторна логіка для Edge Cases та інших штатів (без циклів!)
    # Якщо штат NY, але округ не знайдено (ті самі 10 точок)
    ny_edge_mask = (points_gdf['state_name'] == 'New York') & (points_gdf['county_name'].isna())
    points_gdf.loc[ny_edge_mask, 'county_name'] = 'New York'

    # Якщо це інший штат (NJ, PA тощо)
    other_state_mask = (points_gdf['state_name'].notna()) & (points_gdf['state_name'] != 'New York')
    points_gdf.loc[other_state_mask, 'county_name'] = points_gdf['state_name']

    # 7. Очищення: видаляємо геометрію та допоміжні колонки для повернення чистого DF
    result_df = pd.DataFrame(points_gdf.drop(columns=['geometry', 'state_name']))
    
    # Тепер у вас є колонки 'city_name' та 'county_name' для всієї таблиці
    return result_df

def get_tax_info(city, county, subtotal):
    # 1. Початкові значення
    res = {
        "state_rate": 0.0,
        "county_rate": 0.0,
        "city_rate": 0.0,
        "special_rate": 0.0,
        "code": None
    }

    if not county:
        return Tax(
            composite_tax_rate=0.0,
            tax_amount=0.0,
            jurisdictions=None,
            state_rate=0.0,
            county_rate=0.0,
            city_rate=0.0,
            special_rate=0.0
        )

    city_clean = str(city).strip().lower() if city else ""
    county_clean = str(county).strip().lower()

    # 2. Обробка інших штатів та Edge Cases
    other_states_rates = {
        "new jersey": {"total": 0.06625, "code": "NJ"},
        "connecticut": {"total": 0.0635, "code": "CT"},
        "vermont": {"total": 0.06, "code": "VT"},
        "pennsylvania": {"total": 0.06, "code": "PA"},
        "massachusetts": {"total": 0.0625, "code": "MA"},
        "new york": {"total": 0.08, "code": "NY_ED"} 
    }

    if county_clean in other_states_rates:
        rate_data = other_states_rates[county_clean]
        # Для простоти вважаємо це як county_rate у цих випадках
        total_rate = rate_data["total"]
        return Tax(
            composite_tax_rate=total_rate,
            tax_amount=round(subtotal * total_rate, 2),
            jurisdictions=rate_data["code"],
            state_rate=0.0, # або розбити, якщо потрібно
            county_rate=total_rate,
            city_rate=0.0,
            special_rate=0.0
        )

    # 3. Логіка для Нью-Йорка
    nyc_boroughs = ["bronx", "kings", "new york", "queens", "richmond"]
    if county_clean in nyc_boroughs:
        city_clean = "new york city"

    # Пошук по ny_tax_rates (твоя існуюча логіка)
    for entry in ny_tax_rates:
        if not entry.get("is_city") and county_clean == entry["clean_name"].lower():
            res["county_rate"] = entry.get("rate", 0.0)
            res["code"] = entry.get("code")
            break

    for entry in ny_tax_rates:
        if entry.get("is_city") and city_clean == entry["clean_name"].lower():
            res["city_rate"] = entry.get("rate", 0.0)
            if entry.get("code"): res["code"] = entry["code"]
            break

    for entry in ny_tax_rates:
        if entry.get("type") == "special" and county_clean in entry.get("applicable_counties", []):
            res["special_rate"] = entry.get("rate", 0.0)
            break

    # Базова ставка штату NY
    res["state_rate"] = 0.04 if (res["county_rate"] > 0 or res["city_rate"] > 0) else 0.0

    # 4. Створення фінального об'єкта Tax
    total_rate = res["state_rate"] + res["county_rate"] + res["city_rate"] + res["special_rate"]
    
    return Tax(
        composite_tax_rate=total_rate,
        tax_amount=round(subtotal * total_rate, 2),
        jurisdictions=res["code"][:5] if res["code"] else None, # Обрізаємо до String(5)
        state_rate=res["state_rate"],
        county_rate=res["county_rate"],
        city_rate=res["city_rate"],
        special_rate=res["special_rate"]
    )