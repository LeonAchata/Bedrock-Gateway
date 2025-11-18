# 🐳 Guía de Despliegue con Docker

Esta guía te ayudará a desplegar el Bedrock Gateway usando Docker para desarrollo local o producción.

## 📋 Requisitos Previos

- Docker instalado (v20.10+)
- Docker Compose instalado (v2.0+)
- Credenciales AWS con acceso a Bedrock
- 2GB RAM disponible

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Contenido del `.env`:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
LOG_LEVEL=INFO
```

### 2. Build y Run

```bash
# Opción A: Docker Compose (recomendado)
docker-compose up -d

# Opción B: Docker directo
docker build -t bedrock-gateway:latest .
docker run -d --env-file .env bedrock-gateway:latest
```

### 3. Verificar

```bash
# Ver logs
docker-compose logs -f bedrock-gateway

# Ver contenedores activos
docker-compose ps
```

## 🛠️ Comandos Útiles

### Build

```bash
# Build normal
docker-compose build

# Build sin caché (forzar rebuild)
docker-compose build --no-cache

# Build con tag específico
docker build -t bedrock-gateway:v1.0.0 .
```

### Run

```bash
# Iniciar en background
docker-compose up -d

# Iniciar con logs visibles
docker-compose up

# Reiniciar servicio
docker-compose restart

# Detener servicio
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

### Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver últimas 100 líneas
docker-compose logs --tail=100

# Logs de un servicio específico
docker-compose logs -f bedrock-gateway
```

### Debug

```bash
# Entrar al contenedor
docker-compose exec bedrock-gateway /bin/bash

# Ejecutar comando en el contenedor
docker-compose exec bedrock-gateway python -m src.server

# Ver procesos dentro del contenedor
docker-compose exec bedrock-gateway ps aux

# Ver variables de entorno
docker-compose exec bedrock-gateway env
```

## 📊 Monitoreo

### Ver Recursos

```bash
# CPU y memoria en tiempo real
docker stats bedrock-gateway

# Información del contenedor
docker inspect bedrock-gateway

# Logs del sistema
docker-compose logs --tail=50 bedrock-gateway
```

### Health Check

```bash
# Verificar estado del contenedor
docker-compose ps

# El output debe mostrar:
# NAME                 STATUS
# bedrock-gateway      Up (healthy)
```

## 🔧 Configuración Avanzada

### Variables de Entorno Completas

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_SESSION_TOKEN=optional_session_token

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE=1000

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json, text

# Performance
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT_SECONDS=300
```

### Resource Limits

Editar `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4'      # Máximo 4 CPUs
      memory: 4G     # Máximo 4GB RAM
    reservations:
      cpus: '1'      # Mínimo 1 CPU
      memory: 1G     # Mínimo 1GB RAM
```

### Volúmenes Persistentes

```yaml
volumes:
  # Logs persistentes
  - ./logs:/logs
  
  # Configuración personalizada
  - ./config:/app/config:ro
  
  # Cache persistente (opcional)
  - cache-volume:/app/cache
```

## 🌐 Despliegue en Producción

### 1. Optimización de Imagen

```dockerfile
# Multi-stage build ya incluido
# Tamaño final: ~150MB
```

### 2. Secrets Management

**Opción A: Docker Secrets** (Docker Swarm)

```bash
# Crear secrets
echo "your_access_key" | docker secret create aws_access_key -
echo "your_secret_key" | docker secret create aws_secret_key -

# Usar en compose
services:
  bedrock-gateway:
    secrets:
      - aws_access_key
      - aws_secret_key
```

**Opción B: Variables de Entorno Encriptadas**

```bash
# Usar AWS Secrets Manager, HashiCorp Vault, etc.
```

### 3. Reverse Proxy (si usas SSE en el futuro)

```yaml
# nginx.conf
upstream bedrock_gateway {
    server bedrock-gateway:8000;
}

server {
    listen 80;
    server_name gateway.example.com;
    
    location / {
        proxy_pass http://bedrock_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Escalado Horizontal

```bash
# Docker Compose
docker-compose up -d --scale bedrock-gateway=3

# Docker Swarm
docker service scale bedrock-gateway=3

# Kubernetes
kubectl scale deployment bedrock-gateway --replicas=3
```

## 🔒 Seguridad

### Best Practices

1. **No incluir credenciales en la imagen**
   - Siempre usar variables de entorno
   - Nunca hacer commit de `.env`

2. **Usuario no-root**
   - El Dockerfile ya usa usuario `gateway`
   - UID: 1000

3. **Network Isolation**
   ```yaml
   networks:
     frontend:
     backend:
       internal: true  # Sin acceso externo
   ```

4. **Read-only filesystem**
   ```yaml
   services:
     bedrock-gateway:
       read_only: true
       tmpfs:
         - /tmp
   ```

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"

```bash
# Linux/Mac
sudo systemctl start docker

# Windows
# Abrir Docker Desktop
```

### Error: "Port already in use"

```bash
# Ver qué usa el puerto
netstat -tulpn | grep 8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"
```

### Error: AWS Credentials

```bash
# Verificar dentro del contenedor
docker-compose exec bedrock-gateway env | grep AWS

# Verificar acceso a Bedrock
docker-compose exec bedrock-gateway \
  python -c "import boto3; print(boto3.client('bedrock-runtime').list_foundation_models())"
```

### Logs no aparecen

```bash
# Verificar volumen de logs
docker volume inspect llm-gateway_logs

# Ver logs directamente
docker-compose logs --tail=100 -f
```

### Contenedor se reinicia constantemente

```bash
# Ver por qué falla
docker-compose logs bedrock-gateway

# Ver exit code
docker inspect bedrock-gateway | grep ExitCode
```

## 📈 Performance Tuning

### 1. Cache Optimization

```env
CACHE_ENABLED=true
CACHE_TTL_SECONDS=7200    # 2 horas
CACHE_MAX_SIZE=5000       # 5000 entradas
```

### 2. Connection Pooling

```python
# Ya incluido en boto3 por defecto
# Max pool connections: 10
```

### 3. Resource Monitoring

```bash
# Prometheus metrics (agregar en el futuro)
# Grafana dashboard
```

## 🚢 CI/CD Pipeline

### GitHub Actions

```yaml
name: Docker Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t bedrock-gateway:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag bedrock-gateway:${{ github.sha }} registry.example.com/bedrock-gateway:latest
          docker push registry.example.com/bedrock-gateway:latest
```

## 📝 Logs

Los logs se guardan en:
- **Contenedor**: stdout (ver con `docker-compose logs`)
- **Host**: `./logs/` (si montaste el volumen)

Formato de logs:
```
2024-01-15 10:30:45 - INFO - BedrockClient initialized
2024-01-15 10:30:50 - INFO - Request: model=nova-pro, tokens=150
2024-01-15 10:30:51 - INFO - Response: cached=false, latency=1234ms
```

## 🎯 Next Steps

1. ✅ Gateway funcionando en Docker
2. ⏳ Agregar métricas Prometheus
3. ⏳ Implementar SSE transport (HTTP endpoint)
4. ⏳ Deploy a AWS ECS/Fargate
5. ⏳ Configurar autoscaling

---

**¿Problemas?** Abre un issue en el repositorio.
