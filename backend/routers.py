from fastapi import APIRouter, HTTPException, Query, UploadFile, Depends
import tax_service as tax_service
import io
from sqlmodel import Session
from models import OrderInput, Order
import pandas as pd
import main
import service

def get_session():
    with Session(main.engine) as session:
        yield session

router = APIRouter()

@router.post('/orders/import')
async def import_csv(file: UploadFile, session: any = Depends(get_session)):
# 1. Валідація формату файлу
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл має бути у форматі CSV")

    contents = await file.read()

    try:
        # Читаємо CSV за допомогою pandas (engine='c' для швидкості)
        df = pd.read_csv(io.BytesIO(contents), engine='c')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка парсингу CSV: {str(e)}")

    # Перевірка наявності необхідних колонок
    required_columns = {'longitude', 'latitude', 'subtotal'}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=422, 
            detail=f"Відсутні обов'язкові колонки: {required_columns - set(df.columns)}"
        )

    # 2. ПАКЕТНИЙ ГЕО-АНАЛІЗ (Оптимізація)
    # find_batch повертає DataFrame з доданими 'city_name' та 'county_name'
    processed_df = tax_service.find_batch(df)

    orders_to_create = []

    # 3. ЦИКЛ СТВОРЕННЯ ОБ'ЄКТІВ
    # Використовуємо itertuples для швидкої ітерації по DataFrame
    for row in processed_df.itertuples(index=False):
        # Якщо точка поза США (county_name буде None), ігноруємо її
        if pd.isna(row.county_name):
            continue

        # Створюємо об'єкт моделі Tax (get_tax_info тепер повертає об'єкт Tax)
        tax_object = tax_service.get_tax_info(
            city=row.city_name,
            county=row.county_name,
            subtotal=float(row.subtotal)
        )

        # Готуємо дані для Order, видаляючи технічні поля find_batch
        order_data = row._asdict()
        
        # Видаляємо поля, яких немає в моделі Order, щоб не було AttributeError
        keys_to_remove = ['city_name', 'county_name', 'state_name', 'Index', 'geometry', 'id']
        for key in keys_to_remove:
            order_data.pop(key, None)

        # Створюємо об'єкт Order
        new_order = Order(**order_data)
        
        # Встановлюємо зв'язок 1-до-1: SQLAlchemy сама зв'яже ID
        new_order.tax = tax_object
        
        orders_to_create.append(new_order)

    # 4. ЗБЕРЕЖЕННЯ В БАЗУ ДАНИХ
    if not orders_to_create:
        raise HTTPException(
            status_code=422, 
            detail="Не знайдено жодного замовлення в межах США"
        )

    try:
        # Використовуємо твій сервіс із bulk_save_objects та батчами
        service.create_orders(orders_to_create, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка запису в базу: {str(e)}")
    
@router.post('/orders')
async def create_order(order: OrderInput, session: any = Depends(get_session)):
    tax = tax_service.calculate_tax(order)
    return service.create_order(order, tax, session)

@router.get('/orders')
async def get_orders(
    limit: int = Query(10, ge=1, le=100), # за замовчуванням 10, макс 100
    offset: int = Query(0, ge=0),
    timestamp: str = Query("newest", enum=["newest", "oldest"]),
    total: str = Query('desc', enum=['asc', 'desc']),
    tax: str = Query("desc", enum=["asc", "desc"]),
    session: Session = Depends(get_session)
):
    orders, total = service.get_orders(
        session=session,
        limit=limit,
        offset=offset,
        timestamp=timestamp,
        total=total,
        tax=tax,
    )
    
    return {
        "data": orders,
        "meta": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "total": total,
            "tax": tax,
            'timestamp': timestamp
        }
    }
