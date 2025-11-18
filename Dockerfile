FROM python:3.13-slim as builder

# Metadatos
LABEL maintainer="your-email@example.com"
LABEL description="Bedrock Gateway - MCP Server for AWS Bedrock Models"

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.13-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AWS_REGION=us-east-1 \
    CACHE_ENABLED=true \
    CACHE_TTL_SECONDS=3600 \
    LOG_LEVEL=INFO

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 gateway && \
    mkdir -p /app /logs && \
    chown -R gateway:gateway /app /logs

# Copiar dependencias desde builder
COPY --from=builder --chown=gateway:gateway /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder --chown=gateway:gateway /usr/local/bin /usr/local/bin

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código fuente
COPY --chown=gateway:gateway src/ ./src/
COPY --chown=gateway:gateway requirements.txt .
COPY --chown=gateway:gateway README.md .

# Cambiar a usuario no-root
USER gateway

# Healthcheck (opcional - descomentar si agregas endpoint HTTP)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD python -c "import sys; sys.exit(0)"

# Exponer puerto (si usas SSE transport en el futuro)
# EXPOSE 8000

# Comando por defecto: ejecutar el MCP server
CMD ["python", "-m", "src.server"]

# ============================================
# Notas de Uso:
# ============================================
#
# 1. Build de la imagen:
#    docker build -t bedrock-gateway:latest .
#
# 2. Run con variables de entorno:
#    docker run --rm \
#      -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
#      -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
#      -e AWS_REGION=us-east-1 \
#      -e CACHE_ENABLED=true \
#      -e LOG_LEVEL=INFO \
#      bedrock-gateway:latest
#
# 3. Run con archivo .env:
#    docker run --rm --env-file .env bedrock-gateway:latest
#
# 4. Run con volumen para logs:
#    docker run --rm \
#      --env-file .env \
#      -v $(pwd)/logs:/logs \
#      bedrock-gateway:latest
#
# 5. Docker Compose (ver docker-compose.yml):
#    docker-compose up -d
#
# ============================================
