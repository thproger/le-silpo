from models import OrderInput
from models import OrderInput, Order, Tax
from sqlmodel import Session
from shapely.geometry import Point
import repository

def create_order(order_input: OrderInput, tax: Tax, sesion: Session) -> Order:
    order = Order(latitude=order_input.latitude, longitude=order_input.longitude, subtotal=order_input.subtotal, tax=tax)
    return repository.create_order(sesion, order)

def create_orders(orders: list[Order], session: Session):
    repository.create_orders(session, orders)

def get_orders(
    session: Session,
    limit: int,
    offset: int,
    timestamp: str,
    tax: str,
    total: str
) -> list[Order]:
    return repository.get_all_orders(session, limit, offset, timestamp=timestamp, tax=tax, total=total)