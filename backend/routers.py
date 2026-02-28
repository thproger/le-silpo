from fastapi import APIRouter, HTTPException, UploadFile, Depends
import services.tax_service as tax_service
import io
from sqlmodel import Session
from models import OrderInput, OrderSchema, Order
import pandas
import main
import services.service

def get_session():
    with Session(main.engine) as session:
        yield session

router = APIRouter()

@router.post('/orders/import', response_model=list[OrderSchema])
async def import_csv(file: UploadFile, session: any = Depends(get_session)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл має бути у форматі CSV")

    contents = await file.read()

    try:
        df = pandas.read_csv(io.BytesIO(contents), engine='c')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Parsing error {str(e)}')
    orders: list[Order] = []
    taxes = []
    errors = []

    if errors:
        raise HTTPException(status_code=422, detail={"message": "Помилки у даних CSV", "errors": errors})

    for row in df.itertuples(index=False):
        tax = tax_service.calculate_tax(row)
        order_data = row._asdict()
        order_data.pop('id', None)
        orders.append(Order(**order_data, tax=tax))
        taxes.append(tax)
    result = services.service.create_orders(orders, session)

    return result

@router.post('/orders')
def create_order(order: OrderInput, session: any = Depends(get_session)):
    tax = tax_service.calculate_tax(order)
    return services.service.create_order(order, tax, session)

@router.get('/orders', response_model=list[OrderSchema])
async def get_orders(session: Session = Depends(get_session)):
    return services.service.get_all_orders(session)