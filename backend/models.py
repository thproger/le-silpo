from pydantic import BaseModel, ConfigDict, NaiveDatetime
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func

class Base(DeclarativeBase):
    pass

class OrderInput(BaseModel):
    latitude: float
    longitude: float
    subtotal: float
    timestamp: datetime | None
    model_config = ConfigDict(from_attributes=True)

class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    subtotal: Mapped[float]
    tax: Mapped[float]


class OrderRead(BaseModel):
    id: int
    latitude: float
    longitude: float
    subtotal: float
    tax: float
    # timestamp: datetime | None # додайте, якщо використовуєте дату

    # Це дозволяє Pydantic читати дані з об'єктів SQLAlchemy (наприклад, з вашого класу Order)
    model_config = ConfigDict(from_attributes=True)