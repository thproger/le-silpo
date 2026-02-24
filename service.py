from geopy.geocoders import Nominatim
import reverse_geocoder as rg
from models import OrderInput
from shapely.geometry import Point
from typing import Union
import main

NYS_TAX_RATES = {
    "New York County": {"county": 0.045, "city": 0.0, "special": 0.00375}, # Мангеттен (8.875%)
    "Kings County": {"county": 0.045, "city": 0.0, "special": 0.00375},    # Бруклін
    "Queens County": {"county": 0.045, "city": 0.0, "special": 0.00375},   # Квінс
    "Erie County": {"county": 0.0475, "city": 0.0, "special": 0.0},        # Баффало (8.75%)
    "Monroe County": {"county": 0.04, "city": 0.0, "special": 0.0},        # Рочестер (8.0%)
    "Albany County": {"county": 0.04, "city": 0.0, "special": 0.0},        # Олбані (8.0%)
    # Додайте інші округи за потреби...
}

STATE_RATE = 0.04



def calculate_tax_with_geopandas(order: any) -> dict:
    """
    Приймає об'єкт замовлення, перевіряє перетин координати з картою 
    та повертає об'єкт з розрахованими податками.
    """
    if main.COUNTIES_GDF is None:
        raise RuntimeError("База даних геометрії не завантажена")

    # 1. Витягуємо дані з об'єкта (підтримує Pydantic та звичайні словники)
    lat = order.latitude if hasattr(order, 'latitude') else order['latitude']
    lon = order.longitude if hasattr(order, 'longitude') else order['longitude']
    subtotal = order.subtotal if hasattr(order, 'subtotal') else order['subtotal']

    # 2. Створюємо геометричну точку Shapely (Увага: формат завжди (Довгота, Широта) -> (X, Y))
    point = Point(lon, lat)

    # 3. ПРОСТОРОВИЙ ПОШУК (Point in Polygon)
    # Шукаємо рядок у GeoDataFrame, полігон якого містить нашу точку
    matching_county = main.COUNTIES_GDF[main.COUNTIES_GDF.geometry.contains(point)]

    # 4. Визначаємо назву округу
    if not matching_county.empty:
        # Беремо значення з першого знайденого збігу (припускаємо, що колонка називається 'county_name')
        # Змініть 'county_name' на ту назву колонки, яка реально є у вашому GeoJSON файлі
        county_name = str(matching_county.iloc[0].get('county_name', 'Unknown'))
    else:
        county_name = 'Unknown' # Точка впала в океан або за межі штату

    # 5. Отримуємо ставки для знайденого округу
    rates = NYS_TAX_RATES.get(county_name, {"county": 0.0, "city": 0.0, "special": 0.0})
    
    # 6. Розраховуємо підсумкову ставку та суми податків
    composite_rate = STATE_RATE + rates['county'] + rates['city'] + rates['special']
    

    tax_amount = round(subtotal * composite_rate, 2)
    total_amount = round(subtotal + tax_amount, 2)

    # 7. Формуємо результат податків
    return {
        "composite_tax_rate": round(composite_rate, 5),
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "breakdown": {
            "state_rate": STATE_RATE,
            "county_rate": rates['county'],
            "city_rate": rates['city'],
            "special_rates": rates['special']
        },
        "jurisdictions": f"NYS, {county_name} County" if county_name != 'Unknown' else "Out of NYS"
    }
