"""Nodo LangGraph reutilizable para consultar Bedrock Gateway.

Este módulo proporciona un nodo estándar de LangGraph que puede
integrarse en cualquier grafo de agente para consultar modelos de
Bedrock a través del gateway MCP.
"""

import logging
from typing import TypedDict, Annotated, Sequence
from typing_extensions import TypedDict

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not installed. Run: pip install langgraph")

# Cliente Bedrock Gateway
from bedrock_client import BedrockGatewayClient

logger = logging.getLogger(__name__)


# ==================== STATE DEFINITION ====================

class AgentState(TypedDict):
    """Estado base para agentes que usan el Bedrock Gateway.
    
    Este TypedDict define la estructura mínima necesaria para
    usar el nodo de consulta LLM. Los agentes pueden extenderlo
    con campos adicionales según sus necesidades.
    
    Attributes:
        messages: Lista de mensajes de la conversación (formato OpenAI)
        model: Nombre del modelo Bedrock a usar (ej: "nova-pro", "claude-3-5-sonnet")
        response: Última respuesta del modelo (opcional)
        temperature: Temperatura para la generación (default: 0.7)
        max_tokens: Máximo de tokens a generar (default: 2000)
        usage: Información de uso de tokens (optional)
        cost_usd: Costo estimado de la última llamada (optional)
    """
    messages: Annotated[Sequence[dict], add_messages]
    model: str
    response: str
    temperature: float
    max_tokens: int
    usage: dict
    cost_usd: float


# ==================== LLM NODE ====================

async def llm_consultation_node(state: AgentState) -> AgentState:
    """Nodo de LangGraph para consultar modelos Bedrock.
    
    Este nodo:
    1. Extrae mensajes y modelo del estado
    2. Se conecta al Bedrock Gateway vía MCP
    3. Envía la consulta al modelo especificado
    4. Actualiza el estado con la respuesta
    
    Args:
        state: Estado del agente con mensajes y modelo
        
    Returns:
        Estado actualizado con la respuesta del modelo
        
    Raises:
        ValueError: Si falta el modelo o los mensajes
        Exception: Si hay error en la comunicación con el gateway
        
    Ejemplo de uso en un grafo:
        ```python
        workflow = StateGraph(AgentState)
        workflow.add_node("llm", llm_consultation_node)
        workflow.add_edge("llm", END)
        workflow.set_entry_point("llm")
        
        app = workflow.compile()
        result = await app.ainvoke({
            "messages": [{"role": "user", "content": "Hola"}],
            "model": "nova-pro",
            "temperature": 0.7,
            "max_tokens": 2000
        })
        ```
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph is required. Install: pip install langgraph")
    
    # Validar estado
    if not state.get("model"):
        raise ValueError("State must include 'model' field")
    
    if not state.get("messages"):
        raise ValueError("State must include 'messages' field")
    
    model = state["model"]
    messages = state["messages"]
    temperature = state.get("temperature", 0.7)
    max_tokens = state.get("max_tokens", 2000)
    
    logger.info(
        f"LLM Node - Consulting {model} with {len(messages)} messages"
    )
    
    try:
        # Conectar al gateway y generar respuesta
        async with BedrockGatewayClient() as client:
            result = await client.generate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        # Extraer respuesta
        response_content = result["content"]
        usage = result["usage"]
        cost_usd = result["estimated_cost_usd"]
        
        logger.info(
            f"LLM Node - Response received: "
            f"{usage['total_tokens']} tokens, "
            f"${cost_usd:.6f}"
        )
        
        # Actualizar estado
        return {
            **state,
            "messages": [
                *messages,
                {"role": "assistant", "content": response_content}
            ],
            "response": response_content,
            "usage": usage,
            "cost_usd": cost_usd
        }
        
    except Exception as e:
        logger.error(f"LLM Node - Error: {str(e)}")
        raise


# ==================== VARIANTES DE NODO ====================

async def llm_node_with_system_prompt(
    state: AgentState,
    system_prompt: str
) -> AgentState:
    """Nodo LLM que añade un system prompt automáticamente.
    
    Útil para agentes especializados que siempre usan el mismo
    system prompt.
    
    Args:
        state: Estado del agente
        system_prompt: System prompt a añadir al inicio
        
    Returns:
        Estado actualizado con respuesta
    """
    # Añadir system prompt si no existe
    messages = state["messages"]
    if not messages or messages[0].get("role") != "system":
        messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]
    
    # Llamar al nodo normal con mensajes modificados
    modified_state = {**state, "messages": messages}
    return await llm_consultation_node(modified_state)


def create_llm_node_for_model(model_name: str):
    """Factory para crear nodo LLM con modelo fijo.
    
    Útil para agentes que siempre usan el mismo modelo.
    
    Args:
        model_name: Nombre del modelo Bedrock a usar
        
    Returns:
        Función de nodo configurada para ese modelo
        
    Ejemplo:
        ```python
        # Crear nodo especializado para Claude
        claude_node = create_llm_node_for_model("claude-3-5-sonnet")
        
        workflow.add_node("analyze", claude_node)
        ```
    """
    async def fixed_model_node(state: AgentState) -> AgentState:
        modified_state = {**state, "model": model_name}
        return await llm_consultation_node(modified_state)
    
    fixed_model_node.__name__ = f"llm_node_{model_name.replace('-', '_')}"
    return fixed_model_node


# ==================== HELPER FUNCTIONS ====================

def create_simple_llm_graph(model: str) -> StateGraph:
    """Crear un grafo LangGraph simple con un solo nodo LLM.
    
    Útil para testing o casos de uso simples de consulta directa.
    
    Args:
        model: Nombre del modelo Bedrock
        
    Returns:
        Grafo compilado listo para ejecutar
        
    Ejemplo:
        ```python
        app = create_simple_llm_graph("nova-pro")
        result = await app.ainvoke({
            "messages": [{"role": "user", "content": "Hola"}],
            "model": "nova-pro"
        })
        print(result["response"])
        ```
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph is required")
    
    workflow = StateGraph(AgentState)
    
    # Añadir nodo LLM
    workflow.add_node("llm", llm_consultation_node)
    
    # Conectar flujo
    workflow.set_entry_point("llm")
    workflow.add_edge("llm", END)
    
    return workflow.compile()


async def quick_query(
    model: str,
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """Helper para hacer una consulta rápida sin crear grafo.
    
    Args:
        model: Modelo Bedrock a usar
        prompt: Pregunta o prompt
        temperature: Temperatura
        max_tokens: Tokens máximos
        
    Returns:
        Respuesta del modelo (solo el contenido)
        
    Ejemplo:
        ```python
        response = await quick_query(
            model="nova-pro",
            prompt="¿Cuál es la capital de Francia?"
        )
        print(response)  # "La capital de Francia es París."
        ```
    """
    app = create_simple_llm_graph(model)
    
    result = await app.ainvoke({
        "messages": [{"role": "user", "content": prompt}],
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens
    })
    
    return result["response"]


__all__ = [
    "AgentState",
    "llm_consultation_node",
    "llm_node_with_system_prompt",
    "create_llm_node_for_model",
    "create_simple_llm_graph",
    "quick_query"
]
