from pydantic import BaseModel, NaiveDatetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class OrderInput(BaseModel):
    latitude: float
    longitude: float
    subtotal: float
    # timestamp: NaiveDatetime | None

class Breakdown(BaseModel):
    state_rate: float
    county_rate: float
    city_rate: float
    special_rates: float

class TaxResponse(BaseModel):
    composite_tax_rate: float
    tax_amount: float
    total_amount: float
    breakdown: Breakdown
    jurisdictions: str

class Order(Base):
    __tablename__ = 'order'
    id: Mapped[int] = mapped_column(primary_key=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    subtotal: Mapped[float]