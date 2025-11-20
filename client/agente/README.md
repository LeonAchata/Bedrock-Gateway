# 🔌 Integración con Bedrock Gateway

Este directorio contiene todo lo necesario para que tus agentes de LangGraph se comuniquen con el Bedrock Gateway usando el protocolo MCP.

## 📦 Contenido

- **`bedrock_client.py`**: Cliente MCP para comunicación stdio con el gateway
- **`llm_node.py`**: Nodo reutilizable de LangGraph para consultas LLM
- **`example_agent.py`**: 5 ejemplos completos de uso
- **`requirements.txt`**: Dependencias necesarias

## 🚀 Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

## 💡 Uso Rápido

### Opción 1: Consulta Directa (sin grafo)

```python
from llm_node import quick_query

# Pregunta simple
response = await quick_query(
    model="nova-pro",
    prompt="¿Cuál es la capital de Francia?"
)
print(response)
```

### Opción 2: Nodo en LangGraph

```python
from langgraph.graph import StateGraph, END
from llm_node import AgentState, llm_consultation_node

# Crear grafo
workflow = StateGraph(AgentState)
workflow.add_node("llm", llm_consultation_node)
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)

app = workflow.compile()

# Ejecutar
result = await app.ainvoke({
    "messages": [{"role": "user", "content": "Hola"}],
    "model": "nova-pro",
    "temperature": 0.7,
    "max_tokens": 2000
})

print(result["response"])
```

### Opción 3: Cliente MCP Directo

```python
from bedrock_client import BedrockGatewayClient

async with BedrockGatewayClient() as client:
    # Generar completion
    response = await client.generate(
        model="claude-3-5-sonnet",
        messages=[{"role": "user", "content": "Explica recursión"}],
        temperature=0.7
    )
    print(response["content"])
    
    # Listar modelos disponibles
    models = await client.list_models()
    for model in models:
        print(f"- {model['name']}: ${model['input_cost_per_1k']:.6f}/1K")
```

## 🏗️ Estructura del State

El `AgentState` base incluye:

```python
class AgentState(TypedDict):
    messages: list[dict]      # Conversación (formato OpenAI)
    model: str                # Modelo Bedrock (ej: "nova-pro")
    response: str             # Última respuesta del modelo
    temperature: float        # Temperatura (default: 0.7)
    max_tokens: int           # Tokens máximos (default: 2000)
    usage: dict               # Info de tokens usados
    cost_usd: float           # Costo estimado en USD
```

**Puedes extenderlo** con tus propios campos:

```python
class MyAgentState(AgentState):
    task_type: str
    context: str
    results: list[str]
```

## 🎯 Modelos Disponibles

| Modelo | Nombre | Mejor Para | Costo (1K tokens) |
|--------|--------|------------|-------------------|
| **Nova Pro** | `nova-pro` | General purpose, análisis | $0.0008 / $0.0032 |
| **Nova Lite** | `nova-lite` | Consultas rápidas, bajo costo | $0.00006 / $0.00024 |
| **Nova Micro** | `nova-micro` | Tareas simples, ultra rápido | $0.000035 / $0.00014 |
| **Claude 3.5 Sonnet** | `claude-3-5-sonnet` | Código, razonamiento complejo | $0.003 / $0.015 |
| **Claude 3 Haiku** | `claude-3-haiku` | Respuestas rápidas | $0.00025 / $0.00125 |
| **Llama 3.3 70B** | `llama-3-3-70b` | Open source, versátil | $0.00099 / $0.00099 |
| **Mistral Large 2** | `mistral-large-2` | Multilingüe, razonamiento | $0.002 / $0.006 |

Ver lista completa: `await client.list_models()`

## 📚 Ejemplos Completos

El archivo `example_agent.py` incluye 5 ejemplos:

1. **Consulta Simple**: Uso directo sin crear grafo
2. **Agente de Un Nodo**: Grafo básico con un solo nodo LLM
3. **Agente Multi-Nodo**: Routing dinámico según tipo de consulta
4. **Conversación Multi-Turno**: Mantener contexto entre turnos
5. **Agentes Especializados**: Nodos con modelos fijos

```bash
# Ejecutar todos los ejemplos
python example_agent.py
```

## 🔧 Configuración Avanzada

### Gateway en Otro Directorio

```python
client = BedrockGatewayClient(
    gateway_command="python",
    gateway_args=["-m", "src.server"],  # Ruta relativa al gateway
    gateway_env={
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "...",
        "AWS_REGION": "us-east-1"
    }
)
```

### Nodo con System Prompt Fijo

```python
from llm_node import llm_node_with_system_prompt

async def my_specialized_node(state):
    return await llm_node_with_system_prompt(
        state,
        system_prompt="Eres un experto en Python. Responde con código limpio."
    )
```

### Nodo con Modelo Fijo

```python
from llm_node import create_llm_node_for_model

# Crear nodo que siempre usa Claude
claude_node = create_llm_node_for_model("claude-3-5-sonnet")

workflow.add_node("code_analysis", claude_node)
```

## 🛠️ Integración en Tu Proyecto

### 1. Copiar archivos necesarios

```bash
cp bedrock_client.py your_project/
cp llm_node.py your_project/
```

### 2. Instalar dependencias

```bash
pip install mcp langgraph langchain-core
```

### 3. Usar en tu agente

```python
from llm_node import AgentState, llm_consultation_node
from langgraph.graph import StateGraph, END

# Tu estado personalizado
class MyAgentState(AgentState):
    custom_field: str

# Tu grafo
workflow = StateGraph(MyAgentState)
workflow.add_node("llm", llm_consultation_node)
workflow.add_node("process", my_custom_node)

# Flujo
workflow.set_entry_point("llm")
workflow.add_edge("llm", "process")
workflow.add_edge("process", END)

app = workflow.compile()
```

## 📊 Monitoreo

```python
# Obtener estadísticas del gateway
async with BedrockGatewayClient() as client:
    stats = await client.get_stats()
    
    print(f"Total requests: {stats['metrics']['total_requests']}")
    print(f"Cache hit rate: {stats['cache']['hit_rate']:.2%}")
    print(f"Total tokens: {stats['metrics']['total_tokens']}")
    print(f"Total cost: ${stats['metrics']['total_cost_usd']:.4f}")
```

## ⚠️ Troubleshooting

### Error: "MCP SDK not installed"
```bash
pip install mcp
```

### Error: "LangGraph not installed"
```bash
pip install langgraph
```

### Error: "Not connected to gateway"
- Verifica que el gateway esté corriendo
- Confirma las rutas en `gateway_command` y `gateway_args`

### Error: AWS Credentials
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### Gateway no responde
- Verifica logs del gateway
- Confirma que boto3 esté instalado en el gateway
- Revisa permisos IAM para Bedrock

## 🎓 Patrones Recomendados

### 1. Un Modelo por Agente
```python
# Agente especializado en código
workflow.add_node("code", create_llm_node_for_model("claude-3-5-sonnet"))

# Agente para consultas rápidas
workflow.add_node("quick", create_llm_node_for_model("nova-lite"))
```

### 2. Routing Dinámico
```python
async def router(state):
    if "código" in state["messages"][-1]["content"]:
        state["model"] = "claude-3-5-sonnet"
    else:
        state["model"] = "nova-pro"
    return state
```

### 3. Conversaciones con Contexto
```python
# Mantener todos los mensajes en el state
state["messages"].append({"role": "user", "content": user_input})
result = await app.ainvoke(state)
state = result  # Preservar contexto
```

## 📝 Licencia

Este código es parte del proyecto Bedrock Gateway y puede ser usado libremente en tus agentes.

---

**¿Preguntas?** Revisa `example_agent.py` para casos de uso completos.
