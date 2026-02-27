from fastapi import HTTPException, UploadFile, Depends
from pydantic import ValidationError
import main
import tax_service
import io
from models import OrderInput
from sqlmodel import Session
import csv

@main.app.get('/orders')
def get_orders():
    return {"Hello": "world"}

@main.app.post('/orders')
async def create_order(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл має бути у форматі CSV")

    contents = await file.read()

    try:
        decoded_content = contents.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Помилка кодування файлу. Використовуйте UTF-8.")


    csv_file = io.StringIO(decoded_content)
    csv_reader = csv.DictReader(csv_file)
    orders: list[OrderInput] = []
    errors = []

    # 4. Проходимося по кожному рядку і створюємо об'єкти
    for row_number, row in enumerate(csv_reader, start=1):
        try:
            # Розпаковуємо словник (рядок з CSV) прямо в Pydantic модель
            order = OrderInput(**row)
            orders.append(order)
        except ValidationError as e:
            # Якщо дані невалідні (наприклад, замість числа текст), записуємо помилку
            errors.append({
                "row": row_number,
                "errors": e.errors()
            })

    # 5. Якщо були помилки валідації, повертаємо їх клієнту
    if errors:
        raise HTTPException(status_code=422, detail={"message": "Помилки у даних CSV", "errors": errors})

    return [tax_service.calculate_tax(order) for order in orders]


@main.app.post('/orders')
def create_order(order: OrderInput):
    return tax_service.calculate_tax(order)
