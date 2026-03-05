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
        session.add_all(batch)   # ORM автоматично створює FK для .tax
        session.commit()
        session.expire_all()     # дозволяє працювати joinedload після вставки

from sqlalchemy import asc, desc, select, func
from sqlalchemy.orm import contains_eager

def get_orders(session: Session, limit: int, offset: int, sort_by: str, order: str):
    # 1. Рахуємо загальну кількість
    count_stmt = select(func.count()).select_from(Order)
    total_count = session.exec(count_stmt).scalar()

    # 2. Базовий запит із завантаженням зв'язку
    stmt = select(Order).outerjoin(Order.tax).options(contains_eager(Order.tax))

    # 3. Визначаємо напрямок (функцію asc або desc)
    direction = asc if order == "asc" else desc

    # 4. Фільтруємо сортування: вибираємо ТІЛЬКИ ОДНЕ поле
    if sort_by == "timestamp":
        stmt = stmt.order_by(direction(Order.timestamp))
    elif sort_by == "total":
        stmt = stmt.order_by(direction(Order.subtotal))
    elif sort_by == "tax":
        # Сортуємо по полю з приєднаної таблиці Tax
        stmt = stmt.order_by(direction(Tax.tax_amount))

    # 5. Пагінація
    stmt = stmt.offset(offset).limit(limit)
    
    orders = session.exec(stmt).scalars().all()
    
    return orders, total_count