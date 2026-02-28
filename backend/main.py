import geopandas as gpd
from sqlmodel import create_engine, SQLModel, Session
from fastapi import FastAPI
import os
from contextlib import asynccontextmanager
from routers import router
from models import Base, Order
from fastapi.middleware.cors import CORSMiddleware

nevshtati = 0

PASSWORD = os.getenv('DATABASE_PASSWORD')
mysql_uri = f'mysql://lesilpo_buildinch:d916b27f00dd38a8659e0b92edd7ae9791583999@ybbegs.h.filess.io:3306/lesilpo_buildinch'
engine = create_engine(mysql_uri)
print("Creating tables...")
Order.__table__.create(bind=engine, checkfirst=True)
print("Checking metadata:", Base.metadata.tables.keys())
SQLModel.metadata.create_all(engine)
print("Tables created!")

with open('Cities_Towns.geojson', 'r') as file:
    cities = gpd.read_file(file)

cities['geometry'] = cities.geometry.make_valid()
cities = cities.to_crs(epsg=3857)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield SQLModel.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)