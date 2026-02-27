from models import Order
from sqlmodel import Session, select

def create_order(session: Session, order: Order) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def create_orders(session: Session, orders: list[Order]) -> list[Order]:
    # db_orders = [Order.model_validate(order) for order in orders]
    session.add_all(orders)
    session.commit()

    return orders

def get_all_orders(session: Session) -> list[Order]:
    return session.exec(select(Order)).all()