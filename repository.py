from models import Order, OrderInput
from sqlmodel import Session

def create_order(session: Session, order: OrderInput) -> Order:
    db_order = Order.model_validate(order)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order

def create_orders(session: Session, orders: list[OrderInput]) -> list[Order]:
    db_orders = [Order.model_validate(order) for order in orders]
    session.add_all(db_orders)
    session.commit()

    return db_orders
