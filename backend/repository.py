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

def get_all_orders(
    session: Session,
    limit: int,
    offset: int,
    timestamp: str,
    tax: str,
    total: str
) -> list[Order]:
    count_statement = select(func.count()).select_from(Order)
    count = session.exec(count_statement).one()
    # 1. Базовий запит з outer join, щоб підвантажити .tax
    stmt = select(Order).outerjoin(Order.tax).options(contains_eager(Order.tax))

    # 2. Сортування
    order_clauses = []

    # timestamp сортування
    if timestamp == "newest":
        order_clauses.append(desc(Order.timestamp))
    else:  # oldest
        order_clauses.append(asc(Order.timestamp))

    # subtotal
    if total == "asc":
        order_clauses.append(asc(Order.subtotal))
    else:
        order_clauses.append(desc(Order.subtotal))

    # tax_amount (якщо tax не None)
    if tax == "asc":
        order_clauses.append(asc(Tax.tax_amount))
    else:
        order_clauses.append(desc(Tax.tax_amount))

    stmt = stmt.order_by(*order_clauses).offset(offset).limit(limit)

    # 3. Виконання
    orders = session.exec(stmt).all()  # тут .tax автоматично заповниться завдяки contains_eager

    return orders, count