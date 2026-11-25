from models import Order, Tax
from sqlmodel import Session, select, func, asc, desc, insert
from sqlalchemy.orm import joinedload, contains_eager

def create_order(session: Session, order: Order) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def create_orders(session: Session, orders: list[Order], batch_size = 1000):
    for i in range(0, len(orders), batch_size):
        batch = orders[i:i + batch_size]
        session.add_all(batch)
        session.commit()
        session.expire_all()

from sqlalchemy import asc, desc, select, func
from sqlalchemy.orm import contains_eager

def get_orders(session: Session, limit: int, offset: int, sort_by: str, order: str):
    count_stmt = select(func.count()).select_from(Order)
    total_count = session.exec(count_stmt).scalar()

    stmt = select(Order).outerjoin(Order.tax).options(contains_eager(Order.tax))
    direction = asc if order == "asc" else desc

    if sort_by == "timestamp":
        stmt = stmt.order_by(direction(Order.timestamp))
    elif sort_by == "total":
        stmt = stmt.order_by(direction(Order.subtotal))
    elif sort_by == "tax":
        stmt = stmt.order_by(direction(Tax.tax_amount))

    stmt = stmt.offset(offset).limit(limit)
    orders = session.exec(stmt).scalars().all()
    
    return orders, total_count