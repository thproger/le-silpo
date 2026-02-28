from models import Order, Tax
from sqlmodel import Session, select, func
from sqlalchemy.orm import joinedload

def create_order(session: Session, order: Order) -> Order:
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def create_orders(session: Session, orders: list[Order]) -> list[Order]:
    try:
        session.bulk_save_objects(orders)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e
        
    return orders

def get_all_orders(session: Session, limit: int, offset: int) -> list[Order]:
    total_statement = select(func.count()).select_from(Order)
    total = session.exec(total_statement).one()
    
    # 2. Отримуємо самі дані з лімітом та офсетом
    data_statement = (
        select(Order)
        .join(Tax)
        .options(joinedload(Order.tax))  # Завантажуємо Tax відразу
        .order_by(Order.id.desc())        # Нові зверху
        .offset(offset)
        .limit(limit)
    )
    
    orders = session.exec(data_statement).all()
    return orders, total