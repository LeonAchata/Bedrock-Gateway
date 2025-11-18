# LLM Gateway (MCP Server)

**Gateway centralizado para múltiples modelos de AWS Bedrock a través del Model Context Protocol (MCP)**

Este proyecto implementa un servidor MCP que permite a agentes y workflows de IA comunicarse con **15+ modelos foundation de AWS Bedrock** (Nova, Claude, Llama, Mistral, etc.) a través de una interfaz MCP estandarizada.

## 🎯 Propósito

El LLM Gateway actúa como **puente universal** entre workflows externos de IA y los modelos foundation de Bedrock, proporcionando:

- **Acceso unificado** a 15+ modelos de Bedrock (Nova, Claude, Llama, Mistral)
- **Cada agente elige su modelo** según sus necesidades (hardcodeado en el agente)
- **Caching inteligente** de respuestas para reducir costos y latencia
- **Métricas detalladas** de uso, costos y rendimiento
- **Interfaz MCP estándar** para conexión universal de agentes

## 🏗️ Arquitectura

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Agent A     │       │  Agent B     │       │  Agent C     │
│  (nova-pro)  │       │  (claude)    │       │  (llama)     │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                       │
       │        MCP Protocol (stdio/SSE)              │
       └──────────────────────┼───────────────────────┘
                              ▼
                   ┌────────────────────┐
                   │   LLM Gateway      │
                   │   (MCP Server)     │
                   │                    │
                   │  ┌──────────────┐  │
                   │  │   Router     │  │
                   │  ├──────────────┤  │
                   │  │   Cache      │  │
                   │  ├──────────────┤  │
                   │  │   Metrics    │  │
                   │  └──────────────┘  │
                   └─────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐   ┌──────────┐
        │  Nova   │    │ Claude  │   │  Llama   │
        │  Models │    │ Models  │   │  Models  │
        └─────────┘    └─────────┘   └──────────┘
              AWS Bedrock Foundation Models
```

## 📁 Estructura del Proyecto

```
llm-gateway/
├── src/
│   ├── server.py           # Servidor FastMCP principal
│   ├── config.py           # Configuración (solo AWS Bedrock)
│   │
│   ├── models/             # 🆕 Catálogo de modelos Bedrock
│   │   ├── bedrock_models.py  # 15+ FMs con pricing
│   │   └── __init__.py
│   │
│   ├── bedrock/            # 🆕 Cliente Bedrock universal
│   │   ├── bedrock_client.py  # Cliente único para todos los modelos
│   │   └── __init__.py
│   │
│   ├── mcp/                # MCP Tools
│   │   ├── tools.py        # generate, list_models, get_stats
│   │   └── __init__.py
│   │
│   ├── core/               # Lógica de negocio
│   │   ├── router.py       # Enrutamiento a modelos
│   │   ├── cache.py        # Sistema de caché
│   │   ├── metrics.py      # Tracking de métricas
│   │   └── __init__.py
│   │
│   └── utils/              # Utilidades
│       ├── logger.py       # Logging centralizado
│       ├── validators.py   # Validaciones
│       └── __init__.py
│
├── ParaAgente/             # 🎯 Integración para agentes LangGraph
│   ├── bedrock_client.py   # Cliente MCP (stdio)
│   ├── llm_node.py         # Nodo reutilizable LangGraph
│   ├── example_agent.py    # 5 ejemplos completos
│   ├── requirements.txt    # Dependencias del agente
│   └── README.md           # Guía de integración
│
├── Dockerfile              # 🐳 Imagen Docker para producción
├── docker-compose.yml      # Despliegue fácil con Docker Compose
├── .dockerignore           # Exclusiones de build
├── DOCKER_DEPLOYMENT.md    # 📖 Guía completa de Docker
│
├── requirements.txt        # Dependencias del gateway
├── .env.example            # Template de variables de entorno
├── mcp_config.example.json # Configuración MCP de ejemplo
├── AGENT_EXAMPLES.md       # Ejemplos de configuración de agentes
└── README.md               # Este archivo
│
├── requirements.txt
├── .env.example
├── mcp_config.example.json
├── AGENT_EXAMPLES.md       # 🆕 Ejemplos de configuración
└── README.md
```

## 🚀 Instalación

### 1. Clonar e instalar dependencias

```bash
cd llm-gateway
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crear archivo `.env` con tus credenciales AWS:

```bash
# AWS Bedrock (única configuración necesaria)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Cache y métricas
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
METRICS_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

### 3. Ejecutar el servidor

```bash
python -m src.server
```

## 📋 Modelos Disponibles

El gateway soporta **15+ modelos de Bedrock**:

### Amazon Nova
- `nova-pro` - Avanzado, razonamiento superior ($0.0008/$0.0032 per 1K)
- `nova-lite` - Rápido y económico ($0.00006/$0.00024 per 1K)
- `nova-micro` - Ultra rápido, básico ($0.000035/$0.00014 per 1K)

### Anthropic Claude
- `claude-3-5-sonnet` - Más inteligente ($0.003/$0.015 per 1K)
- `claude-3-5-haiku` - Más rápido ($0.001/$0.005 per 1K)
- `claude-3-opus` - Más poderoso ($0.015/$0.075 per 1K)
- `claude-3-sonnet` - Balanceado ($0.003/$0.015 per 1K)
- `claude-3-haiku` - Eficiente ($0.00025/$0.00125 per 1K)

### Meta Llama
- `llama-3-3-70b` - Último modelo 70B ($0.00065/$0.00065 per 1K)
- `llama-3-2-90b` - Multimodal con visión ($0.0008/$0.0008 per 1K)
- `llama-3-2-11b` - Pequeño multimodal ($0.00016/$0.00016 per 1K)
- `llama-3-1-70b` - 70B parámetros ($0.00099/$0.00099 per 1K)
- `llama-3-1-8b` - Pequeño y eficiente ($0.00022/$0.00022 per 1K)

### Mistral
- `mistral-large-2` - Flagship, razonamiento avanzado ($0.003/$0.009 per 1K)
- `mistral-small` - Rápido y económico ($0.001/$0.003 per 1K)

**Ver lista completa:** `await mcp.call_tool("list_models", {})`

## 🔌 Conexión desde Agentes

### Concepto Clave

**Cada agente especifica su modelo en el código**, no en la configuración. El gateway es un único punto de entrada para todos los modelos de Bedrock.

### Configuración MCP (igual para todos los agentes)

```json
{
  "mcpServers": {
    "llm-gateway": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret"
      }
    }
  }
}
```

### Agent A - Usa Nova Pro

```python
# Este agente siempre usa nova-pro
response = await session.call_tool(
    "generate",
    {
        "model": "nova-pro",  # <-- Modelo hardcodeado en el agente
        "messages": [{"role": "user", "content": "Tarea compleja..."}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
)
```

### Agent B - Usa Claude 3.5 Sonnet

```python
# Este agente siempre usa claude-3-5-sonnet
response = await session.call_tool(
    "generate",
    {
        "model": "claude-3-5-sonnet",  # <-- Modelo diferente
        "messages": [{"role": "user", "content": "Análisis profundo..."}]
    }
)
```

### Agent C - Usa Llama 3.3 70B

```python
# Este agente siempre usa llama-3-3-70b
response = await session.call_tool(
    "generate",
    {
        "model": "llama-3-3-70b",  # <-- Otro modelo
        "messages": [{"role": "user", "content": "Tarea general..."}]
    }
)
```

**Ver más ejemplos:** [AGENT_EXAMPLES.md](AGENT_EXAMPLES.md)

### Ejemplo completo desde un agente (Python)

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def use_llm_gateway():
    # Conectar al gateway
    async with stdio_client("python", ["-m", "src.server"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializar
            await session.initialize()
            
            # Listar modelos disponibles
            models = await session.call_tool("list_models", {})
            print(f"Available: {len(models)} models")
            
            # Generar completion con el modelo específico del agente
            response = await session.call_tool(
                "generate",
                {
                    "model": "nova-pro",  # <-- El agente elige su modelo
                    "messages": [
                        {"role": "user", "content": "¿Qué es IA?"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            print(f"Response: {response['content']}")
            print(f"Tokens: {response['usage']['total_tokens']}")
            print(f"Cost: ${response['estimated_cost_usd']:.6f}")
            print(f"Cached: {response['cached']}")
            print(f"Latency: {response['latency_ms']:.2f}ms")
```

## 🛠️ Herramientas MCP Disponibles

### 1. `generate`

Genera completions usando cualquier modelo de Bedrock.

**Parámetros:**
- `model` (str): Nombre corto del modelo (ej: "nova-pro", "claude-3-5-sonnet", "llama-3-3-70b")
- `messages` (list): Lista de mensajes con 'role' y 'content'
- `temperature` (float): Temperatura de muestreo (0.0-2.0)
- `max_tokens` (int): Máximo de tokens a generar

**Retorna:**
```json
{
  "content": "Respuesta generada...",
  "model": "nova-pro",
  "model_id": "us.amazon.nova-pro-v1:0",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 50,
    "total_tokens": 60
  },
  "finish_reason": "stop",
  "cached": false,
  "latency_ms": 1234.56,
  "estimated_cost_usd": 0.001234
}
```

### 2. `list_models`

Lista todos los modelos de Bedrock disponibles con pricing.

**Retorna:**
```json
[
  {
    "name": "nova-pro",
    "model_id": "us.amazon.nova-pro-v1:0",
    "description": "Advanced multimodal AI model with superior reasoning",
    "context_window": 300000,
    "input_cost_per_1k": 0.0008,
    "output_cost_per_1k": 0.0032,
    "supports_system": true,
    "max_tokens": 5000
  },
  ...
]
```

### 3. `get_stats`

Obtiene estadísticas del gateway (métricas y caché).

**Retorna:**
```json
{
  "metrics": {
    "total_requests": 100,
    "total_tokens": 50000,
    "total_cost_usd": 1.23,
    "cache_hit_rate_percent": 45.5,
    "average_latency_ms": 1234.5,
    "requests_by_model": {
      "nova-pro": 50,
      "claude-3-5-sonnet": 30,
      "llama-3-3-70b": 20
    }
  },
  "cache": {
    "current_size": 50,
    "max_size": 1000,
    "enabled": true
  }
}
```

## 📊 Características

### ✅ Implementadas

- ✅ Servidor FastMCP con protocolo estándar
- ✅ **15+ modelos de Bedrock** (Nova, Claude, Llama, Mistral)
- ✅ **Cliente Bedrock universal** - un solo cliente para todos los modelos
- ✅ **Cada agente elige su modelo** - hardcodeado en el código del agente
- ✅ Sistema de caché con TTL
- ✅ Métricas detalladas por modelo (requests, tokens, costos, latencias)
- ✅ Validaciones centralizadas
- ✅ Logging estructurado
- ✅ Estimación de costos automática con pricing real

### 🔮 Futuras

- 🔜 Rate limiting por agente
- 🔜 Persistencia de métricas (base de datos)
- 🔜 Dashboard web de monitoreo
- 🔜 Streaming de respuestas
- 🔜 Soporte para modelos con imágenes (multimodales)

## 📝 Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | - |
| `AWS_REGION` | AWS Region | us-east-1 |
| `CACHE_ENABLED` | Habilitar caché | true |
| `CACHE_TTL` | TTL del caché (segundos) | 3600 |
| `CACHE_MAX_SIZE` | Tamaño máximo del caché | 1000 |
| `METRICS_ENABLED` | Habilitar métricas | true |
| `LOG_LEVEL` | Nivel de logging | INFO |

## ❓ FAQ

### ¿Por qué solo Bedrock y no otros proveedores?

Este gateway está optimizado para **entornos empresariales** donde Bedrock ofrece:
- 15+ modelos bajo una sola infraestructura
- Seguridad y compliance empresarial
- Sin límites de rate por usuario (límites por cuenta AWS)
- Pricing predecible y sin cargos ocultos

### ¿Cómo decide cada agente qué modelo usar?

El modelo se especifica **en el código del agente**, no en configuración:

```python
# Agente A
response = await mcp.call_tool("generate", {"model": "nova-pro", ...})

# Agente B  
response = await mcp.call_tool("generate", {"model": "claude-3-5-sonnet", ...})

# Agente C
response = await mcp.call_tool("generate", {"model": "llama-3-3-70b", ...})
```

### ¿Puedo tener múltiples agentes conectados al mismo gateway?

**Sí**, es el caso de uso principal. Todos los agentes se conectan al mismo gateway MCP, pero cada uno especifica su modelo preferido. El gateway:
- Cachea respuestas compartidas entre agentes
- Trackea métricas por modelo
- Optimiza costos con caché inteligente

### ¿Cómo agrego un nuevo modelo de Bedrock?

Edita `src/models/bedrock_models.py` y agrega el modelo al diccionario `BEDROCK_MODELS`. Ejemplo:

```python
"mi-modelo": BedrockModel(
    model_id="aws.mi-modelo-v1:0",
    name="Mi Modelo Nuevo",
    description="Descripción",
    context_window=128000,
    input_cost_per_1k=0.001,
    output_cost_per_1k=0.002,
    supports_system=True,
    max_tokens=4096
)
```

## 🐳 Despliegue con Docker

### Quick Start Local

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus AWS credentials

# 2. Build y run con Docker Compose
docker-compose up -d

# 3. Ver logs
docker-compose logs -f
```

### Build Manual

```bash
# Build de la imagen
docker build -t bedrock-gateway:latest .

# Run con variables de entorno
docker run -d \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_REGION=us-east-1 \
  -e CACHE_ENABLED=true \
  bedrock-gateway:latest
```

### Características Docker

- ✅ Multi-stage build (imagen optimizada ~150MB)
- ✅ Usuario no-root (seguridad)
- ✅ Volúmenes persistentes para logs
- ✅ Health checks configurables
- ✅ Resource limits (CPU/memoria)
- ✅ Compatible con Docker Compose y Kubernetes

**📖 Guía completa:** Ver [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) para:
- Configuración avanzada
- Escalado horizontal
- Monitoreo y debugging
- Despliegue en producción (ECS/Fargate)
- Troubleshooting completo

## 🎯 Integración con Agentes LangGraph

### Quick Start

La carpeta `ParaAgente/` contiene todo lo necesario:

```bash
# 1. Instalar dependencias del agente
cd ParaAgente
pip install -r requirements.txt

# 2. Usar el nodo LLM en tu grafo
from llm_node import AgentState, llm_consultation_node
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("llm", llm_consultation_node)
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)

app = workflow.compile()

# 3. Ejecutar
result = await app.ainvoke({
    "messages": [{"role": "user", "content": "Hola"}],
    "model": "nova-pro"
})
print(result["response"])
```

### Contenido de ParaAgente/

- **`bedrock_client.py`**: Cliente MCP (stdio) para el gateway
- **`llm_node.py`**: Nodo reutilizable de LangGraph
- **`example_agent.py`**: 5 ejemplos completos
- **`README.md`**: Guía de integración detallada

**📖 Documentación completa:** Ver [ParaAgente/README.md](ParaAgente/README.md)

## 🆘 Soporte

Para problemas o preguntas:
1. Ver ejemplos en [AGENT_EXAMPLES.md](AGENT_EXAMPLES.md)
2. Ver integración con LangGraph en [ParaAgente/README.md](ParaAgente/README.md)
3. Ver despliegue Docker en [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
4. Revisar logs con `LOG_LEVEL=DEBUG`
5. Verificar credenciales AWS en `.env`
6. Crear un issue en el repositorio

---

**Nota**: Este es un servidor MCP puro. No expone endpoints REST. Los agentes deben conectarse usando el protocolo MCP (stdio o SSE).
