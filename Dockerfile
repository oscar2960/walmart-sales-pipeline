# ==========================================================================
# Dockerfile - Walmart Sales Analytics App
# ==========================================================================
FROM python:3.11-slim

LABEL maintainer="Proyecto Académico DevOps"
LABEL description="Pipeline CI/CD - Aplicación de análisis de ventas Walmart"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Capa de dependencias separada del código para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Usuario no privilegiado (buena práctica de seguridad en contenedores)
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import socket,os; socket.create_connection((os.getenv('DB_HOST','postgres'), int(os.getenv('DB_PORT','5432'))), timeout=3)" || exit 1

CMD ["python", "-m", "app.main"]
