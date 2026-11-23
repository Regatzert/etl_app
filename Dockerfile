FROM python:3.12-slim

# Evita archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Evita buffering de logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema necesarias para PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt /app/

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . /app/

# Puerto de Django
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]