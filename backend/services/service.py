from models import OrderInput
from models import OrderInput, Order, Tax
from sqlmodel import Session
from shapely.geometry import Point
import repository

def create_order(order_input: OrderInput, tax: Tax, sesion: Session) -> Order:
    order = Order(latitude=order_input.latitude, longitude=order_input.longitude, subtotal=order_input.subtotal, tax=tax)
    return repository.create_order(sesion, order)

def create_orders(orders: list[Order], session: Session) -> list[Order]:
    return repository.create_orders(session, orders)

def get_all_orders(session: Session) -> list[Order]:
    return repository.get_all_orders(session)