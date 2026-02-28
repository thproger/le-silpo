from models import Order, Tax
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

def create_order(session: Session, order: Order) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def create_orders(session: Session, orders: list[Order]) -> list[Order]:
    session.add_all(orders)
    session.commit()

    return orders

def get_all_orders(session: Session) -> list[Order]:
    return session.execute(select(Order).join(Tax).options(joinedload(Order.tax))).scalars().all()