# Usa la imagen de python
FROM python:3.12-slim

# Directorio de trabajo principal
WORKDIR /app

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPIAR TODO EL PROYECTO
# Esto incluirá tu carpeta app/data/cache si está ahí
COPY . .

# EXPLICACIÓN: Creamos/Aseguramos permisos para la caché
RUN chmod -R 777 /app/app/data/cache

# Variables de entorno
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Comando para arrancar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]