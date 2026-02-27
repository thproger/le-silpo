FROM python:3.11-slim

# 2. Системні залежності для MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 3. Робоча директорія в контейнері
WORKDIR /app

# 4. Копіюємо requirements.txt (він може бути в корені або в папці backend)
# Якщо він у папці backend, пиши: COPY backend/requirements.txt .
COPY backend/requirements.txt .

# 5. Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# 6. Копіюємо вміст папки backend у поточну директорію контейнера (/app)
COPY backend/ .

# 7. Експонуємо порт
EXPOSE 8000

# 8. Запуск. Зверни увагу: якщо main.py був у backend/, 
# то тепер він лежить прямо в /app, тому шлях "main:app"
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]