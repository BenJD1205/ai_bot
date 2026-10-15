FROM python:3.11-slim

WORKDIR /app

# Tránh ghi bytecode và ép flush log ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Chạy container và thoát 0
ENTRYPOINT ["python", "main.py"]