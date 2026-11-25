from models import OrderInput, Tax
from shapely.geometry import Point
import main
import geopandas as gpd
import pandas as pd
from tax import ny_tax_rates

def calculate_tax(order: OrderInput) -> Tax:
    city, county = find(Point(order.longitude, order.latitude))
    return get_tax_info(city, county, order.subtotal)

def find(point: Point):
    point_gdf = gpd.GeoDataFrame(
        geometry=[point],
        crs="EPSG:4326"
    )
    if main.usa.crs is not None:
        point_gdf = point_gdf.to_crs(main.usa.crs)
    state_match = gpd.sjoin(point_gdf, main.usa, how="left", predicate="within")

    if state_match.empty or pd.isna(state_match.iloc[0]['name']):
        return None, None
    
    state_name = state_match.iloc[0]['name']
    point_gdf = point_gdf.drop(columns=['index_right'], errors='ignore')
    
    county_match = gpd.sjoin(point_gdf, main.counties, how="left", predicate="within")
    county = None
    if not county_match.empty and not pd.isna(county_match.iloc[0]['COUNTY_NAME']):
        county = county_match.iloc[0]['COUNTY_NAME']

    # Довбані 10 точок
    if state_name == "New York" and county is None:
        return None, 'New York'
    elif state_name != 'New York':
        return None, state_name
    
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
    lon = pd.to_numeric(df['longitude'], errors='coerce')
    lat = pd.to_numeric(df['latitude'], errors='coerce')
    
    geometry = [Point(xy) for xy in zip(lon, lat)]
    points_gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs="EPSG:4326")
    
    if main.usa.crs is not None:
        points_gdf = points_gdf.to_crs(main.usa.crs)

    points_gdf = gpd.sjoin(points_gdf, main.usa[['name', 'geometry']], how="left", predicate="within")
    points_gdf = points_gdf.rename(columns={'name': 'state_name'}).drop(columns=['index_right'])

    points_gdf = gpd.sjoin(points_gdf, main.counties[['COUNTY_NAME', 'geometry']], how="left", predicate="within")
    points_gdf = points_gdf.drop(columns=['index_right'])

    points_gdf = gpd.sjoin(points_gdf, main.cities[['NAME', 'geometry']], how="left", predicate="within")
    points_gdf = points_gdf.rename(columns={'NAME': 'city_name', 'COUNTY_NAME': 'county_name'}).drop(columns=['index_right'])

    ny_edge_mask = (points_gdf['state_name'] == 'New York') & (points_gdf['county_name'].isna())
    points_gdf.loc[ny_edge_mask, 'county_name'] = 'New York'

    other_state_mask = (points_gdf['state_name'].notna()) & (points_gdf['state_name'] != 'New York')
    points_gdf.loc[other_state_mask, 'county_name'] = points_gdf['state_name']

    result_df = pd.DataFrame(points_gdf.drop(columns=['geometry', 'state_name']))
    
    return result_df

def get_tax_info(city, county, subtotal):
    total_rate = 4
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
            special_rate=0.0,
            total_amount=round(subtotal*total_rate*0.01, 2) + subtotal
        )

    city_clean = str(city).strip().lower() if city else ""
    county_clean = str(county).strip().lower()

    other_states_rates = {
        "new jersey": {"total": 6.625, "code": "NJ"},
        "connecticut": {"total": 6.35, "code": "CT"},
        "vermont": {"total": 6, "code": "VT"},
        "pennsylvania": {"total": 6, "code": "PA"},
        "massachusetts": {"total": 625, "code": "MA"},
        "new york": {"total": 8, "code": "NY_ED"} 
    }

    if county_clean in other_states_rates:
        rate_data = other_states_rates[county_clean]
        total_rate = rate_data["total"]
        return Tax(
            composite_tax_rate=total_rate,
            tax_amount=round(subtotal * total_rate, 2),
            jurisdictions=rate_data["code"],
            state_rate=0.04, # або розбити, якщо потрібно
            county_rate=total_rate,
            city_rate=0.0,
            special_rate=0.0,
            total_amount=round(subtotal*total_rate, 2) + subtotal
        )

    nyc_boroughs = ["bronx", "kings", "new york", "queens", "richmond"]
    if county_clean in nyc_boroughs:
        city_clean = "new york city"

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

    res["state_rate"] = 4 if (res["county_rate"] > 0 or res["city_rate"] > 0) else 0.0

    total_rate = res["state_rate"] + res["county_rate"] + res["city_rate"] + res["special_rate"]
    
    return Tax(
        composite_tax_rate=total_rate,
        tax_amount=round(subtotal * total_rate*0.01, 2),
        jurisdictions=res["code"][:5] if res["code"] else None,
        state_rate=res["state_rate"],
        county_rate=res["county_rate"],
        city_rate=res["city_rate"],
        special_rate=res["special_rate"],
        total_amount=round(subtotal * total_rate*0.01, 2)+subtotal
    )