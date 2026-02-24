from contextlib import asynccontextmanager

from pydantic import ValidationError
from models import OrderInput
from fastapi import FastAPI, File, HTTPException, UploadFile
import geopandas as gpd
from sqlmodel import create_engine, select, SQLModel
from models import Order, TaxResponse
import service
import csv
import os
import io

PASSWORD = os.getenv('DATABASE_PASSWORD')
mysql_uri = f'mysql://avnadmin:{PASSWORD}@mysql-284693bc-ftcserhiy-b36b.j.aivencloud.com:25042/defaultdb'
engine = create_engine(mysql_uri)
try:
    COUNTIES_GDF = gpd.read_file('Greene_County_Tax_Parcels_-8841005964405968865.geojson')
    # Переводимо в стандартну систему координат GPS (широта/довгота)
    COUNTIES_GDF = COUNTIES_GDF.to_crs("EPSG:4326")
except Exception as e:
    print(f"Помилка завантаження карти: {e}")
    COUNTIES_GDF = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    SQLModel.metadata.create_all(engine)

app = FastAPI(lifespan=lifespan)

@app.get('/orders')
def get_orders():
    return {"Hello": "world"}

@app.post('/orders')
async def create_order(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл має бути у форматі CSV")

    contents = await file.read()

    try:
        decoded_content = contents.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Помилка кодування файлу. Використовуйте UTF-8.")


    csv_file = io.StringIO(decoded_content)
    csv_reader = csv.DictReader(csv_file)
    orders: list[OrderInput] = []
    errors = []

    # 4. Проходимося по кожному рядку і створюємо об'єкти
    for row_number, row in enumerate(csv_reader, start=1):
        try:
            # Розпаковуємо словник (рядок з CSV) прямо в Pydantic модель
            order = OrderInput(**row)
            orders.append(order)
        except ValidationError as e:
            # Якщо дані невалідні (наприклад, замість числа текст), записуємо помилку
            errors.append({
                "row": row_number,
                "errors": e.errors()
            })

    # 5. Якщо були помилки валідації, повертаємо їх клієнту
    if errors:
        raise HTTPException(status_code=422, detail={"message": "Помилки у даних CSV", "errors": errors})

    return [service.calculate_tax_with_geopandas(order) for order in orders]
