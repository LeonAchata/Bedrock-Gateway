# LLM Gateway - Agent Configuration Examples

## Ejemplo 1: Agente con un modelo específico pre-configurado

Cada agente puede tener su propio modelo de Bedrock configurado. El agente simplemente llama al gateway sin especificar el modelo.

### Agent A - Usa Nova Pro (para tareas complejas)

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

**Código del Agente A:**
```python
# Este agente siempre usa nova-pro
response = await session.call_tool(
    "generate",
    {
        "model": "nova-pro",  # <-- Modelo hardcodeado en el agente
        "messages": [{"role": "user", "content": "Tarea compleja..."}]
    }
)
```

---

### Agent B - Usa Claude 3.5 Sonnet (para razonamiento avanzado)

**Configuración:** (misma configuración MCP)

**Código del Agente B:**
```python
# Este agente siempre usa claude-3-5-sonnet
response = await session.call_tool(
    "generate",
    {
        "model": "claude-3-5-sonnet",  # <-- Modelo hardcodeado en el agente
        "messages": [{"role": "user", "content": "Análisis complejo..."}]
    }
)
```

---

### Agent C - Usa Llama 3.3 70B (para tareas generales)

**Código del Agente C:**
```python
# Este agente siempre usa llama-3-3-70b
response = await session.call_tool(
    "generate",
    {
        "model": "llama-3-3-70b",  # <-- Modelo hardcodeado en el agente
        "messages": [{"role": "user", "content": "Tarea general..."}]
    }
)
```

---

## Ejemplo 2: Agente dinámico (elige modelo según la tarea)

Un agente más sofisticado puede decidir qué modelo usar según el contexto:

```python
class IntelligentAgent:
    def __init__(self, mcp_session):
        self.session = mcp_session
    
    async def process_task(self, task_type, message):
        # Elegir modelo según el tipo de tarea
        if task_type == "complex_reasoning":
            model = "claude-3-5-sonnet"
        elif task_type == "fast_simple":
            model = "nova-micro"
        elif task_type == "balanced":
            model = "nova-pro"
        elif task_type == "long_context":
            model = "claude-3-opus"
        else:
            model = "llama-3-3-70b"
        
        response = await self.session.call_tool(
            "generate",
            {
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )
        
        return response
```

---

## Ejemplo 3: Múltiples agentes con el mismo gateway

Todos los agentes se conectan al **mismo LLM Gateway**, pero cada uno especifica su modelo preferido:

```python
# ====== AGENT A: Investigación (usa Claude para análisis profundo) ======
class ResearchAgent:
    async def research(self, topic):
        response = await mcp.call_tool("generate", {
            "model": "claude-3-5-sonnet",
            "messages": [{"role": "user", "content": f"Investiga: {topic}"}]
        })
        return response["content"]

# ====== AGENT B: Generación rápida (usa Nova Micro para velocidad) ======
class FastGeneratorAgent:
    async def generate_quick(self, prompt):
        response = await mcp.call_tool("generate", {
            "model": "nova-micro",
            "messages": [{"role": "user", "content": prompt}]
        })
        return response["content"]

# ====== AGENT C: Multilingüe (usa Llama para varios idiomas) ======
class MultilingualAgent:
    async def translate(self, text, target_lang):
        response = await mcp.call_tool("generate", {
            "model": "llama-3-3-70b",
            "messages": [{"role": "user", "content": f"Translate to {target_lang}: {text}"}]
        })
        return response["content"]
```

---

## Modelos Disponibles en el Gateway

| Nombre | Model ID | Descripción | Costo (Input/Output per 1K) |
|--------|----------|-------------|----------------------------|
| **nova-pro** | us.amazon.nova-pro-v1:0 | Avanzado, razonamiento superior | $0.0008 / $0.0032 |
| **nova-lite** | us.amazon.nova-lite-v1:0 | Rápido y económico | $0.00006 / $0.00024 |
| **nova-micro** | us.amazon.nova-micro-v1:0 | Ultra rápido, básico | $0.000035 / $0.00014 |
| **claude-3-5-sonnet** | us.anthropic.claude-3-5-sonnet... | Más inteligente de Claude | $0.003 / $0.015 |
| **claude-3-5-haiku** | us.anthropic.claude-3-5-haiku... | Más rápido de Claude | $0.001 / $0.005 |
| **llama-3-3-70b** | us.meta.llama3-3-70b-instruct... | Llama último modelo | $0.00065 / $0.00065 |
| **llama-3-2-90b** | us.meta.llama3-2-90b-instruct... | Multimodal con visión | $0.0008 / $0.0008 |
| **mistral-large-2** | mistral.mistral-large-2407... | Razonamiento avanzado | $0.003 / $0.009 |

Para ver la lista completa: `await mcp.call_tool("list_models", {})`

---

## Configuración del Agente

### En el archivo `mcp_config.json` del agente:

```json
{
  "mcpServers": {
    "llm-gateway": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret-key",
        "CACHE_ENABLED": "true",
        "METRICS_ENABLED": "true"
      }
    }
  }
}
```

### En el código del agente:

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# Conectar al gateway
async with stdio_client("python", ["-m", "src.server"]) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # El agente especifica qué modelo usar
        response = await session.call_tool(
            "generate",
            {
                "model": "nova-pro",  # <-- Modelo específico del agente
                "messages": [{"role": "user", "content": "Tu pregunta aquí"}]
            }
        )
```

---

## Resumen

✅ **Cada agente especifica su modelo en el código** (`model="nova-pro"`)  
✅ **Un solo gateway atiende múltiples agentes** con diferentes modelos  
✅ **Todos los modelos son de Bedrock** (15+ modelos disponibles)  
✅ **Cache y métricas compartidas** entre todos los agentes  
✅ **Costo-eficiente**: Elige el modelo adecuado para cada tarea
