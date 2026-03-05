from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey, String
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class Base(DeclarativeBase):
    pass

class TaxBreakdown(BaseModel):
    state_rate: float
    county_rate: float
    city_rate: float
    special_rates: float

    class Config:
        from_attributes = True

class OrderInput(BaseModel):
    latitude: float
    longitude: float
    subtotal: float
    timestamp: datetime | None
    model_config = ConfigDict(from_attributes=True)

class Tax(Base):
    __tablename__ = 'taxes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), unique=True, nullable=False)
    composite_tax_rate: Mapped[float]
    tax_amount: Mapped[float]
    total_amount: Mapped[float]
    jurisdictions: Mapped[str] = mapped_column(String(5), nullable=True)
    
    state_rate: Mapped[float]
    county_rate: Mapped[float]
    city_rate: Mapped[float]
    special_rate: Mapped[float]

    order: Mapped['Order'] = relationship(back_populates='tax')

    model_config = ConfigDict(from_attributes=True)


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())
    subtotal: Mapped[float]
    tax: Mapped['Tax'] = relationship(back_populates='order', uselist=False, cascade='all, delete-orphan')

    @computed_field
    @property
    def total_amount(self) -> float:
        if self.tax:
            return self.subtotal + self.tax.tax_amount
        return self.subtotal
    class Config:
        from_attributes = True


class TaxSchema(BaseModel):
    composite_tax_rate: float
    tax_amount: float
    jurisdictions: str | None
    state_rate: float
    county_rate: float
    special_rate: float
    city_rate: float

    @computed_field
    @property
    def breakdown(self) -> TaxBreakdown:
        return TaxBreakdown(
            state_rate=self.state_rate,
            county_rate=self.county_rate,
            city_rate=self.city_rate,
            special_rates=self.special_rate
        )

    class Config:
        from_attributes = True
        fields = {
            "state_rate": {"exclude": True},
            "county_rate": {"exclude": True},
            'city_rate': {'exclude': True},
            "special_rate": {"exclude": True}
        }

class OrderSchema(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    subtotal: float
    tax: TaxSchema

class OrderPaginationResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: list[OrderSchema]