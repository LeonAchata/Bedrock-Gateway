"""Script de prueba para hacer requests al MCP Gateway en Docker.

Este script te permite probar el gateway directamente enviando requests
a través del protocolo MCP stdio al contenedor Docker.
"""

import asyncio
import json
import subprocess
from typing import Dict, Any


async def test_list_models():
    """Prueba: Listar todos los modelos disponibles."""
    print("\n" + "="*70)
    print("TEST 1: Listar modelos disponibles")
    print("="*70)
    
    # Crear request MCP para list_models
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_models",
            "arguments": {}
        }
    }
    
    # Ejecutar en el contenedor Docker
    result = subprocess.run(
        ["docker", "exec", "-i", "bedrock-gateway", "python", "-m", "src.server"],
        input=json.dumps(request) + "\n",
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.stdout:
        print("\n📋 Modelos disponibles:")
        try:
            response = json.loads(result.stdout.split('\n')[-2])  # Última línea válida
            models = response.get('result', [])
            for model in models:
                print(f"  • {model['name']:20s} - {model['description']}")
                print(f"    Input: ${model['input_cost_per_1k']}/1K | Output: ${model['output_cost_per_1k']}/1K")
        except Exception as e:
            print(f"Error parseando respuesta: {e}")
            print(result.stdout)


async def test_generate_completion(model: str = "nova-lite", prompt: str = "¿Qué es AWS Bedrock?"):
    """Prueba: Generar una completion con un modelo específico.
    
    Args:
        model: Nombre del modelo (nova-lite, nova-pro, claude-3-5-sonnet, etc.)
        prompt: Pregunta o prompt para el modelo
    """
    print("\n" + "="*70)
    print(f"TEST 2: Generar completion con modelo '{model}'")
    print("="*70)
    print(f"💬 Prompt: {prompt}")
    
    # Crear request MCP para generate
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "generate",
            "arguments": {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
    }
    
    print(f"\n🔄 Enviando request al modelo {model}...")
    
    # Ejecutar en el contenedor Docker
    result = subprocess.run(
        ["docker", "exec", "-i", "bedrock-gateway", "python", "-m", "src.server"],
        input=json.dumps(request) + "\n",
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.stdout:
        print("\n✅ Respuesta recibida:")
        try:
            response = json.loads(result.stdout.split('\n')[-2])
            result_data = response.get('result', {})
            
            print(f"\n🤖 Modelo usado: {result_data.get('model', 'N/A')}")
            print(f"📊 Tokens usados: {result_data.get('usage', {}).get('total_tokens', 'N/A')}")
            print(f"💰 Costo: ${result_data.get('cost_usd', 0):.6f}")
            print(f"⏱️  Latencia: {result_data.get('latency_ms', 0):.0f}ms")
            print(f"🔄 Cache hit: {result_data.get('cache_hit', False)}")
            print(f"\n💬 Respuesta del modelo:")
            print("-" * 70)
            print(result_data.get('content', 'No content'))
            print("-" * 70)
            
        except Exception as e:
            print(f"Error parseando respuesta: {e}")
            print(result.stdout)
    
    if result.stderr:
        print(f"\n⚠️  Errores:\n{result.stderr}")


async def test_get_stats():
    """Prueba: Obtener estadísticas del gateway."""
    print("\n" + "="*70)
    print("TEST 3: Obtener estadísticas del gateway")
    print("="*70)
    
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_stats",
            "arguments": {}
        }
    }
    
    result = subprocess.run(
        ["docker", "exec", "-i", "bedrock-gateway", "python", "-m", "src.server"],
        input=json.dumps(request) + "\n",
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.stdout:
        print("\n📊 Estadísticas:")
        try:
            response = json.loads(result.stdout.split('\n')[-2])
            stats = response.get('result', {})
            print(json.dumps(stats, indent=2))
        except Exception as e:
            print(f"Error parseando respuesta: {e}")
            print(result.stdout)


async def main():
    """Ejecutar todos los tests."""
    print("\n🚀 Iniciando tests del MCP Gateway")
    print("="*70)
    
    # Test 1: Listar modelos
    # await test_list_models()
    
    # Test 2: Generar completion con diferentes modelos
    
    # Prueba con Nova Lite (más rápido y barato)
    await test_generate_completion(
        model="nova-lite",
        prompt="Explica en una línea qué es inteligencia artificial."
    )
    
    # Prueba con Nova Pro (más potente)
    # await test_generate_completion(
    #     model="nova-pro",
    #     prompt="Escribe un haiku sobre el océano."
    # )
    
    # Prueba con Claude (excelente para código)
    # await test_generate_completion(
    #     model="claude-3-5-sonnet",
    #     prompt="Escribe una función Python que calcule fibonacci."
    # )
    
    # Test 3: Obtener estadísticas
    # await test_get_stats()
    
    print("\n✅ Tests completados!\n")


if __name__ == "__main__":
    # Forma simple de prueba sin MCP protocol
    print("\n💡 MODO ALTERNATIVO: Prueba directa con Python en el contenedor\n")
    
    # Test directo sin protocolo MCP
    test_code = '''
import asyncio
from src.mcp.tools import generate_completion

async def test():
    result = await generate_completion(
        model="nova-lite",
        messages=[{"role": "user", "content": "¿Qué es AWS Bedrock en una línea?"}],
        temperature=0.7,
        max_tokens=200
    )
    print(f"\\n🤖 Modelo: {result['model']}")
    print(f"📊 Tokens: {result['usage']['total_tokens']}")
    print(f"💰 Costo: ${result['cost_usd']:.6f}")
    print(f"⏱️  Latencia: {result['latency_ms']:.0f}ms")
    print(f"\\n💬 Respuesta:\\n{result['content']}\\n")

asyncio.run(test())
'''
    
    print("Ejecutando test directo en el contenedor...")
    print("="*70)
    
    result = subprocess.run(
        ["docker", "exec", "bedrock-gateway", "python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr and "INFO" not in result.stderr:
        print(f"\n⚠️  Logs/Errores:\n{result.stderr}")
    
    print("\n✅ Test completado!")
    print("\n💡 TIP: Para más tests, descomenta las líneas en main()")
