import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import main  # Твої get_tax_info та завантажені карти
import tax_service

def run_fast_tax_test(input_csv):
    # 1. Завантажуємо CSV
    print("📖 Зчитування файлу...")
    df = pd.read_csv(input_csv)
    
    # 2. Пакетне визначення локацій (метод find_batch)
    print("🌍 Гео-аналіз (пакетна обробка)...")
    processed_df = tax_service.find_batch(df)

    # 3. Кешування розрахунку get_tax_info
    # Оскільки округів лише ~60, ми не хочемо викликати функцію 10 000 разів
    tax_cache = {}

    def get_tax_mapped(row):
        # Якщо немає округу — це точка поза США
        if pd.isna(row['county_name']):
            return None
        
        # Створюємо ключ для кешу
        cache_key = (row['city_name'], row['county_name'])
        
        if cache_key not in tax_cache:
            # Викликаємо твою оригінальну функцію лише один раз для кожної комбінації
            tax_cache[cache_key] = tax_service.get_tax_info(row['city_name'], row['county_name'])
        
        return tax_cache[cache_key]

    print("💰 Розрахунок податків...")
    # Створюємо колонку зі словником податкових даних
    df_tax_data = processed_df.apply(get_tax_mapped, axis=1)

    # 4. Розділення результатів
    # Точки поза США
    outside_mask = df_tax_data.isna()
    outside_usa = processed_df[outside_mask].copy()
    outside_usa.to_csv('points_outside_usa.csv', index=False)

    # Точки з податками
    inside_usa = processed_df[~outside_mask].copy()
    
    # Розгортаємо дані зі словника в окремі колонки
    tax_details = pd.DataFrame(df_tax_data.dropna().tolist(), index=inside_usa.index)
    final_df = pd.concat([inside_usa, tax_details], axis=1)

    # Фінальний розрахунок суми
    final_df['tax_amount'] = (final_df['subtotal'] * final_df['total_rate']).round(2)
    final_df['grand_total'] = (final_df['subtotal'] + final_df['tax_amount']).round(2)

    # 5. Збереження
    final_df.to_csv('orders_with_taxes_fast.csv', index=False)
    
    print("\n" + "="*40)
    print(f"✅ Успішно оброблено: {len(final_df)} замовлень")
    print(f"🌎 Поза США (відфільтровано): {len(outside_usa)}")
    print(f"⏱️ Використано унікальних податкових зон: {len(tax_cache)}")
    print(f"💵 Загальна сума податків: ${final_df['tax_amount'].sum():,.2f}")
    print("="*40)

# Запуск
run_fast_tax_test('BetterMe Test-Input.csv')