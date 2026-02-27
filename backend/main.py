import geopandas as gpd
# from sqlmodel import create_engine, SQLModel, get_session, Session
from fastapi import FastAPI
import os
from contextlib import asynccontextmanager

nevshtati = 0

PASSWORD = os.getenv('DATABASE_PASSWORD')
mysql_uri = f'mysql://avnadmin:{PASSWORD}@mysql-284693bc-ftcserhiy-b36b.j.aivencloud.com:25042/defaultdb'
# engine = create_engine(mysql_uri)

with open('backend/Cities_Towns.geojson', 'r') as file:
    cities = gpd.read_file(file)

cities['geometry'] = cities.geometry.make_valid()
cities = cities.to_crs(epsg=3857)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # SQLModel.metadata.create_all(engine)

app = FastAPI(lifespan=lifespan)

# def get_session():
#     with Session(engine) as session:
#         yield session

from fastapi import HTTPException, UploadFile, Depends
from pydantic import ValidationError
import tax_service
import io
from models import OrderInput
from sqlmodel import Session
import csv

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

    return [tax_service.calculate_tax(order) for order in orders]


@app.post('/ordersssss')
def create_order(order: OrderInput):
    return tax_service.calculate_tax(order)

@app.get('/ne')
def ne():
    return {'ne': nevshtati}