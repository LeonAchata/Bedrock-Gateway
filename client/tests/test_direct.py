"""Cliente de prueba simple para el MCP Gateway.

Este script usa directamente las funciones del gateway sin pasar por MCP,
ideal para testing rápido.
"""

import asyncio
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp.tools import generate_completion, list_available_models, get_gateway_stats
from src.config import settings


async def test_list_models():
    """Test: Listar todos los modelos disponibles."""
    print("\n" + "="*70)
    print("TEST 1: LISTAR MODELOS DISPONIBLES")
    print("="*70 + "\n")
    
    models = list_available_models()
    
    print(f"📋 Total de modelos: {len(models)}\n")
    
    for model in models:
        print(f"🔹 {model['name']:20s}")
        print(f"   Descripción: {model['description']}")
        print(f"   Input:  ${model['input_cost_per_1k']}/1K tokens")
        print(f"   Output: ${model['output_cost_per_1k']}/1K tokens")
        print(f"   Max tokens: {model['max_output_tokens']:,}")
        print()


async def test_generate(model: str, prompt: str):
    """Test: Generar completion con un modelo específico.
    
    Args:
        model: Nombre del modelo (nova-lite, nova-pro, claude-3-5-sonnet, etc.)
        prompt: Pregunta o prompt para el modelo
    """
    print("\n" + "="*70)
    print(f"TEST 2: GENERAR COMPLETION - Modelo: {model}")
    print("="*70)
    print(f"\n💬 Prompt: {prompt}")
    print(f"🔄 Enviando request a AWS Bedrock...")
    
    try:
        result = await generate_completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"\n✅ Respuesta recibida exitosamente!")
        print(f"\n{'─'*70}")
        print(f"🤖 Modelo:        {result.get('model', 'N/A')}")
        print(f"📊 Tokens input:  {result.get('usage', {}).get('input_tokens', 0)}")
        print(f"📊 Tokens output: {result.get('usage', {}).get('output_tokens', 0)}")
        print(f"📊 Tokens total:  {result.get('usage', {}).get('total_tokens', 0)}")
        print(f"💰 Costo estimado: ${result.get('estimated_cost_usd', result.get('cost_usd', 0)):.6f}")
        print(f"⏱️  Latencia:      {result.get('latency_ms', 0):.0f}ms")
        print(f"🔄 Cache hit:     {result.get('cached', result.get('cache_hit', False))}")
        print(f"✅ Finish reason: {result.get('finish_reason', 'N/A')}")
        print(f"{'─'*70}")
        print(f"\n💬 RESPUESTA DEL MODELO:")
        print(f"{'─'*70}")
        print(result.get('content', 'No content available'))
        print(f"{'─'*70}\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_stats():
    """Test: Obtener estadísticas del gateway."""
    print("\n" + "="*70)
    print("TEST 3: ESTADÍSTICAS DEL GATEWAY")
    print("="*70 + "\n")
    
    stats = get_gateway_stats()
    
    print(f"📊 Total requests:     {stats.get('total_requests', 0)}")
    print(f"💰 Total cost:         ${stats.get('total_cost_usd', 0):.6f}")
    print(f"📈 Total tokens:       {stats.get('total_tokens', 0):,}")
    print(f"🔄 Cache hit rate:     {stats.get('cache_hit_rate', 0):.1f}%")
    print(f"⏱️  Avg latency:        {stats.get('avg_latency_ms', 0):.0f}ms")
    print(f"\n🤖 Requests por modelo:")
    for model, count in stats.get('requests_by_model', {}).items():
        print(f"   • {model}: {count}")
    print()


async def main():
    """Ejecutar tests."""
    print("\n🚀 TESTING MCP GATEWAY - AWS BEDROCK")
    print("="*70)
    print(f"🌍 AWS Region:     {settings.AWS_REGION}")
    print(f"🔄 Cache enabled:  {settings.CACHE_ENABLED}")
    print(f"📊 Metrics enabled: {settings.METRICS_ENABLED}")
    print("="*70)
    
    # Test 1: Listar modelos (descomenta si quieres ver todos)
    # await test_list_models()
    
    # Test 2: Probar diferentes modelos
    
    # Nova Lite - El más rápido y económico
    await test_generate(
        model="nova-lite",
        prompt="Explica en 2 líneas qué es inteligencia artificial."
    )
    
    # Nova Pro - Balance entre velocidad y capacidad
    # await test_generate(
    #     model="nova-pro",
    #     prompt="Escribe un haiku sobre el océano."
    # )
    
    # Claude 3.5 Sonnet - Excelente para código y análisis
    # await test_generate(
    #     model="claude-3-5-sonnet",
    #     prompt="Escribe una función Python que calcule el factorial de un número."
    # )
    
    # Llama 3.3 70B - Modelo open source potente
    # await test_generate(
    #     model="llama-3-3-70b",
    #     prompt="¿Cuáles son las ventajas de usar AWS Bedrock?"
    # )
    
    # Test 3: Ver estadísticas acumuladas
    await test_stats()
    
    print("\n✅ Todos los tests completados!")
    print("\n💡 TIP: Ejecuta el script otra vez y verás el cache en acción!")
    print("💡 TIP: Descomenta otros modelos en main() para probarlos\n")


if __name__ == "__main__":
    asyncio.run(main())
