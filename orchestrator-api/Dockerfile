# Dockerfile para el microservicio MCP
# Este Dockerfile está optimizado para Cloud Run con un enfoque multi-stage
# para mantener la imagen final pequeña y eficiente

# ==== STAGE 1: Builder ====
# Usamos una imagen completa para instalar dependencias y compilar extensiones
FROM python:3.11-slim as builder

# Instalar dependencias del sistema necesarias para compilar paquetes Python
# Estas son necesarias para asyncpg y otros paquetes que requieren compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorno virtual para aislar las dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar requirements.txt y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==== STAGE 2: Runtime ====
# Usar una imagen más pequeña para la ejecución final
FROM python:3.11-slim

# Instalar solo las dependencias de runtime necesarias (no las de compilación)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar el entorno virtual desde el builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Crear usuario no privilegiado para mayor seguridad
# Cloud Run recomienda no ejecutar como root
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copiar el código de la aplicación
# Copiamos solo lo necesario para mantener la imagen pequeña
COPY --chown=app:app main.py .
COPY --chown=app:app mcp/ ./mcp/
COPY --chown=app:app agents/ ./agents/
COPY --chown=app:app llm/ ./llm/
COPY --chown=app:app static/ ./static/

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/home/app

# Cloud Run espera que la aplicación escuche en el puerto definido por $PORT
# El puerto por defecto es 8080, pero Cloud Run puede cambiarlo
ENV PORT=8080

# Configuración de logs para Cloud Run
# Cloud Run funciona mejor con logs estructurados que van a stdout
ENV PYTHONUNBUFFERED=1

# Health check para desarrollo local (Cloud Run no usa HEALTHCHECK)
# Pero es útil tenerlo para desarrollo y testing
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:$PORT/health')" || exit 1

# Exponer el puerto (informativo, Cloud Run manejará el puerto real)
EXPOSE $PORT

# Comando para iniciar la aplicación
# Usamos uvicorn con configuración optimizada para producción
CMD uvicorn main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log \
    --no-use-colors \
    --loop uvloop

# ==== NOTAS IMPORTANTES PARA CLOUD RUN ====
#
# 1. PUERTO: Cloud Run asigna automáticamente un puerto y lo pasa en $PORT
# 2. MEMORIA: El contenedor debe usar poca memoria. Si necesitas más, configúralo en Cloud Run
# 3. TIMEOUT: Cloud Run tiene timeout por defecto. Para operaciones largas, aumentar el timeout
# 4. ESCALADO: Cloud Run escala automáticamente. El código debe ser stateless
# 5. LOGS: Todos los logs van a stdout/stderr y aparecen en Cloud Logging
# 6. SECRETOS: Usar Secret Manager para credenciales, no variables de entorno planas
#
# Comandos útiles para desarrollo:
# 
# Construir imagen:
# docker build -t mcp-microservice .
#
# Ejecutar localmente:
# docker run -p 8080:8080 \
#   -e NEO4J_URI=bolt://localhost:7687 \
#   -e NEO4J_USER=neo4j \
#   -e NEO4J_PASSWORD=password \
#   -e POSTGRES_HOST=localhost \
#   -e POSTGRES_PORT=5432 \
#   -e POSTGRES_DB=testdb \
#   -e POSTGRES_USER=postgres \
#   -e POSTGRES_PASSWORD=password \
#   mcp-microservice
#
# Desplegar a Cloud Run:
# gcloud run deploy mcp-microservice \
#   --image gcr.io/YOUR_PROJECT_ID/mcp-microservice \
#   --platform managed \
#   --region us-central1 \
#   --allow-unauthenticated \
#   --set-env-vars="NEO4J_URI=bolt://your-neo4j:7687" \
#   --memory=1Gi \
#   --cpu=1 \
#   --timeout=300 \
#   --max-instances=10