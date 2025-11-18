"""Ejemplo completo de uso del nodo LLM con LangGraph.

Este archivo muestra cómo integrar el nodo de consulta LLM
en un grafo LangGraph real con múltiples nodos y flujo condicional.
"""

import asyncio
import os
from typing import Literal
from llm_node import (
    AgentState,
    llm_consultation_node,
    create_llm_node_for_model,
    quick_query
)

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("⚠️  LangGraph no instalado. Ejecuta: pip install langgraph")


# ==================== EJEMPLO 1: CONSULTA SIMPLE ====================

async def example_simple_query():
    """Ejemplo más simple: una pregunta rápida."""
    print("\n" + "="*60)
    print("EJEMPLO 1: Consulta Simple")
    print("="*60)
    
    response = await quick_query(
        model="nova-lite",
        prompt="¿Cuál es la capital de Perú?"
    )
    
    print(f"\n🤖 Respuesta: {response}\n")


# ==================== EJEMPLO 2: AGENTE CON UN NODO ====================

async def example_single_node_agent():
    """Ejemplo de grafo con un solo nodo LLM."""
    print("\n" + "="*60)
    print("EJEMPLO 2: Agente de Un Solo Nodo")
    print("="*60)
    
    # Crear grafo
    workflow = StateGraph(AgentState)
    workflow.add_node("llm", llm_consultation_node)
    workflow.set_entry_point("llm")
    workflow.add_edge("llm", END)
    
    app = workflow.compile()
    
    # Ejecutar
    result = await app.ainvoke({
        "messages": [
            {"role": "user", "content": "Resume en 2 líneas qué es AWS Bedrock"}
        ],
        "model": "nova-pro",
        "temperature": 0.7,
        "max_tokens": 200
    })
    
    print(f"\n🤖 Modelo: {result['model']}")
    print(f"📊 Tokens: {result['usage']['total_tokens']}")
    print(f"💰 Costo: ${result['cost_usd']:.6f}")
    print(f"\n💬 Respuesta:\n{result['response']}\n")


# ==================== EJEMPLO 3: AGENTE MULTI-NODO ====================

async def router_node(state: AgentState) -> AgentState:
    """Nodo que decide qué modelo usar según la tarea."""
    user_message = state["messages"][-1]["content"].lower()
    
    # Decidir modelo según keywords
    if "código" in user_message or "python" in user_message:
        model = "claude-3-5-sonnet"  # Claude es mejor para código
        print("🔀 Router: Detectado código → usando Claude")
    elif "rápido" in user_message or "simple" in user_message:
        model = "nova-lite"  # Nova Lite es más rápido y barato
        print("🔀 Router: Consulta simple → usando Nova Lite")
    else:
        model = "nova-pro"  # Nova Pro para general purpose
        print("🔀 Router: Consulta general → usando Nova Pro")
    
    return {**state, "model": model}


async def example_multi_node_agent():
    """Ejemplo de grafo con múltiples nodos y routing."""
    print("\n" + "="*60)
    print("EJEMPLO 3: Agente Multi-Nodo con Router")
    print("="*60)
    
    # Crear grafo
    workflow = StateGraph(AgentState)
    
    # Añadir nodos
    workflow.add_node("router", router_node)
    workflow.add_node("llm", llm_consultation_node)
    
    # Conectar flujo
    workflow.set_entry_point("router")
    workflow.add_edge("router", "llm")
    workflow.add_edge("llm", END)
    
    app = workflow.compile()
    
    # Test 1: Pregunta de código
    print("\n📝 Test 1: Pregunta sobre código")
    result1 = await app.ainvoke({
        "messages": [
            {"role": "user", "content": "Escribe un código Python para ordenar una lista"}
        ],
        "temperature": 0.5,
        "max_tokens": 300
    })
    print(f"✅ Modelo usado: {result1['model']}")
    print(f"💬 Respuesta:\n{result1['response'][:150]}...\n")
    
    # Test 2: Pregunta simple
    print("📝 Test 2: Pregunta rápida")
    result2 = await app.ainvoke({
        "messages": [
            {"role": "user", "content": "Dame una respuesta simple: ¿cuánto es 5+5?"}
        ],
        "temperature": 0.3,
        "max_tokens": 100
    })
    print(f"✅ Modelo usado: {result2['model']}")
    print(f"💬 Respuesta: {result2['response']}\n")


# ==================== EJEMPLO 4: CONVERSACIÓN MULTI-TURNO ====================

async def example_conversation():
    """Ejemplo de conversación con múltiples turnos."""
    print("\n" + "="*60)
    print("EJEMPLO 4: Conversación Multi-Turno")
    print("="*60)
    
    # Crear grafo simple
    workflow = StateGraph(AgentState)
    workflow.add_node("llm", llm_consultation_node)
    workflow.set_entry_point("llm")
    workflow.add_edge("llm", END)
    
    app = workflow.compile()
    
    # Estado inicial
    state = {
        "messages": [],
        "model": "nova-pro",
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    # Turno 1
    print("\n👤 Usuario: Hola, soy Juan")
    state["messages"].append({"role": "user", "content": "Hola, soy Juan"})
    result = await app.ainvoke(state)
    print(f"🤖 Asistente: {result['response']}")
    state = result
    
    # Turno 2
    print("\n👤 Usuario: ¿Cuál es mi nombre?")
    state["messages"].append({"role": "user", "content": "¿Cuál es mi nombre?"})
    result = await app.ainvoke(state)
    print(f"🤖 Asistente: {result['response']}")
    state = result
    
    # Turno 3
    print("\n👤 Usuario: Recomiéndame un libro sobre IA")
    state["messages"].append({"role": "user", "content": "Recomiéndame un libro sobre IA"})
    result = await app.ainvoke(state)
    print(f"🤖 Asistente: {result['response']}")
    
    print(f"\n📊 Total tokens usados: {result['usage']['total_tokens']}")
    print(f"💰 Costo total: ${result['cost_usd']:.6f}\n")


# ==================== EJEMPLO 5: MODELOS ESPECÍFICOS ====================

async def example_specialized_agents():
    """Ejemplo con nodos especializados para modelos específicos."""
    print("\n" + "="*60)
    print("EJEMPLO 5: Agentes Especializados")
    print("="*60)
    
    # Crear nodos especializados
    claude_node = create_llm_node_for_model("claude-3-5-sonnet")
    nova_node = create_llm_node_for_model("nova-pro")
    
    # Test Claude (mejor para código)
    print("\n🧠 Claude Sonnet (experto en código):")
    workflow_claude = StateGraph(AgentState)
    workflow_claude.add_node("claude", claude_node)
    workflow_claude.set_entry_point("claude")
    workflow_claude.add_edge("claude", END)
    app_claude = workflow_claude.compile()
    
    result_claude = await app_claude.ainvoke({
        "messages": [
            {"role": "user", "content": "Explica qué es un decorador en Python"}
        ],
        "temperature": 0.5,
        "max_tokens": 300
    })
    print(f"💬 {result_claude['response'][:200]}...")
    
    # Test Nova (mejor para general purpose)
    print("\n⚡ Nova Pro (general purpose):")
    workflow_nova = StateGraph(AgentState)
    workflow_nova.add_node("nova", nova_node)
    workflow_nova.set_entry_point("nova")
    workflow_nova.add_edge("nova", END)
    app_nova = workflow_nova.compile()
    
    result_nova = await app_nova.ainvoke({
        "messages": [
            {"role": "user", "content": "¿Cuáles son los países de América del Sur?"}
        ],
        "temperature": 0.3,
        "max_tokens": 200
    })
    print(f"💬 {result_nova['response']}\n")


# ==================== MAIN ====================

async def main():
    """Ejecutar todos los ejemplos."""
    
    if not LANGGRAPH_AVAILABLE:
        print("❌ LangGraph no está instalado.")
        print("Instala con: pip install langgraph")
        return
    
    print("\n" + "="*60)
    print("🚀 EJEMPLOS DE USO - BEDROCK GATEWAY + LANGGRAPH")
    print("="*60)
    print("\n⚙️  Configuración:")
    print(f"   AWS Region: {os.getenv('AWS_REGION', 'us-east-1')}")
    print(f"   Gateway: Python MCP Server (stdio)")
    
    try:
        # Ejecutar ejemplos
        await example_simple_query()
        await example_single_node_agent()
        await example_multi_node_agent()
        await example_conversation()
        await example_specialized_agents()
        
        print("\n" + "="*60)
        print("✅ Todos los ejemplos completados exitosamente")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Asegurar que AWS credentials estén configuradas
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        print("\n⚠️  WARNING: AWS_ACCESS_KEY_ID no configurada")
        print("Configura tus credentials AWS antes de ejecutar:\n")
        print("  export AWS_ACCESS_KEY_ID=your_key")
        print("  export AWS_SECRET_ACCESS_KEY=your_secret")
        print("  export AWS_REGION=us-east-1\n")
    
    # Ejecutar
    asyncio.run(main())
