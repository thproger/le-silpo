from fastapi import APIRouter, HTTPException, Query, UploadFile, Depends
from typing import Literal
import tax_service as tax_service
import io
from sqlmodel import Session
from models import OrderInput, Order, OrderPaginationResponse
import pandas as pd
import main
import service

def get_session():
    with Session(main.engine) as session:
        yield session

router = APIRouter()

@router.post('/orders/import')
async def import_csv(file: UploadFile, session: any = Depends(get_session)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл має бути у форматі CSV")

    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents), engine='c')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Помилка парсингу CSV: {str(e)}")

    required_columns = {'longitude', 'latitude', 'subtotal'}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=422, 
            detail=f"Відсутні обов'язкові колонки: {required_columns - set(df.columns)}"
        )

    processed_df = tax_service.find_batch(df)

    orders_to_create = []

    for row in processed_df.itertuples(index=False):
        if pd.isna(row.county_name):
            continue

        tax_object = tax_service.get_tax_info(
            city=row.city_name,
            county=row.county_name,
            subtotal=float(row.subtotal)
        )

        order_data = row._asdict()
        
        keys_to_remove = ['city_name', 'county_name', 'state_name', 'Index', 'geometry', 'id']
        for key in keys_to_remove:
            order_data.pop(key, None)

        new_order = Order(**order_data)
        
        new_order.tax = tax_object
        
        orders_to_create.append(new_order)

    if not orders_to_create:
        raise HTTPException(
            status_code=422, 
            detail="Не знайдено жодного замовлення в межах США"
        )

    try:
        service.create_orders(orders_to_create, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка запису в базу: {str(e)}")
    
@router.post('/orders')
async def create_order(order: OrderInput, session: any = Depends(get_session)):
    tax = tax_service.calculate_tax(order)
    return service.create_order(order, tax, session)


@router.get('/orders', response_model=OrderPaginationResponse)
async def get_orders(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: Literal["timestamp", "total", "tax"] = Query("timestamp"),
    order: Literal["asc", "desc"] = Query("desc"),
    session: Session = Depends(get_session)
):
    orders, total_count = service.get_orders(
        session=session,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order
    )

    return OrderPaginationResponse(
        data=orders,
        total=total_count,
        limit=limit,
        offset=offset
    )