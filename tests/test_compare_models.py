"""Test comparativo de diferentes modelos de Bedrock."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp.tools import generate_completion, list_available_models


async def compare_models():
    """Comparar respuestas de diferentes modelos."""
    
    prompt = "Explica qué es AWS Bedrock en máximo 3 líneas."
    
    # Modelos a probar
    models_to_test = [
        "nova-lite",      # Más rápido y económico
        "nova-pro",       # Balance velocidad/calidad
        "claude-3-5-sonnet",  # Excelente razonamiento
    ]
    
    print("\n" + "="*80)
    print("🔬 COMPARATIVA DE MODELOS DE AWS BEDROCK")
    print("="*80)
    print(f"\n💬 Prompt: '{prompt}'\n")
    print("="*80)
    
    results = []
    
    for model in models_to_test:
        print(f"\n🤖 Probando modelo: {model}")
        print("─"*80)
        
        try:
            result = await generate_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            results.append({
                "model": model,
                "success": True,
                "result": result
            })
            
            print(f"✅ Modelo:      {model}")
            print(f"📊 Tokens:     {result['usage']['total_tokens']} (in:{result['usage']['input_tokens']}, out:{result['usage']['output_tokens']})")
            print(f"💰 Costo:      ${result.get('estimated_cost_usd', 0):.6f}")
            print(f"⏱️  Latencia:   {result.get('latency_ms', 0):.0f}ms")
            print(f"🔄 Cache:      {'SÍ' if result.get('cached', False) else 'NO'}")
            print(f"\n💬 Respuesta:")
            print(f"   {result['content']}\n")
            
        except Exception as e:
            print(f"❌ Error con modelo {model}: {e}\n")
            results.append({
                "model": model,
                "success": False,
                "error": str(e)
            })
    
    # Resumen comparativo
    print("\n" + "="*80)
    print("📊 RESUMEN COMPARATIVO")
    print("="*80 + "\n")
    
    successful_results = [r for r in results if r["success"]]
    
    if successful_results:
        print(f"{'Modelo':<20} {'Tokens':<10} {'Costo (USD)':<15} {'Latencia (ms)':<15}")
        print("─"*80)
        
        for r in successful_results:
            result = r["result"]
            model = r["model"]
            tokens = result['usage']['total_tokens']
            cost = result.get('estimated_cost_usd', 0)
            latency = result.get('latency_ms', 0)
            
            print(f"{model:<20} {tokens:<10} ${cost:<14.6f} {latency:<15.0f}")
        
        # Mejor costo/beneficio
        print("\n🏆 RECOMENDACIONES:")
        print("─"*80)
        
        cheapest = min(successful_results, key=lambda x: x["result"].get('estimated_cost_usd', float('inf')))
        fastest = min(successful_results, key=lambda x: x["result"].get('latency_ms', float('inf')))
        
        print(f"💰 Más económico:  {cheapest['model']} (${cheapest['result'].get('estimated_cost_usd', 0):.6f})")
        print(f"⚡ Más rápido:     {fastest['model']} ({fastest['result'].get('latency_ms', 0):.0f}ms)")
        print(f"🎯 Para tareas simples: nova-lite")
        print(f"🎯 Para razonamiento complejo: claude-3-5-sonnet o nova-pro")
    
    print("\n" + "="*80 + "\n")


async def test_with_specific_model():
    """Test con un modelo específico y prompt personalizado."""
    
    print("\n" + "="*80)
    print("🎯 TEST PERSONALIZADO")
    print("="*80 + "\n")
    
    # Cambia estos valores para probar
    model = "nova-pro"  # o "claude-3-5-sonnet", "llama-3-3-70b", etc.
    prompt = "Dame 3 ventajas de usar contenedores Docker."
    
    print(f"🤖 Modelo: {model}")
    print(f"💬 Prompt: {prompt}\n")
    print("─"*80)
    
    result = await generate_completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    print(f"\n✅ RESPUESTA GENERADA:")
    print("─"*80)
    print(f"\n{result['content']}\n")
    print("─"*80)
    print(f"\n📊 Estadísticas:")
    print(f"   • Tokens: {result['usage']['total_tokens']}")
    print(f"   • Costo: ${result.get('estimated_cost_usd', 0):.6f}")
    print(f"   • Latencia: {result.get('latency_ms', 0):.0f}ms")
    print(f"   • Cache: {'SÍ' if result.get('cached', False) else 'NO'}")
    print("\n" + "="*80 + "\n")


async def main():
    """Ejecutar tests."""
    
    print("\n🚀 PRUEBAS DEL BEDROCK GATEWAY")
    
    # Test 1: Comparar varios modelos
    await compare_models()
    
    # Test 2: Ejecuta el mismo prompt de nuevo para ver el cache
    print("\n💡 Ejecutando la comparativa de nuevo para probar el CACHE...")
    await compare_models()
    
    # Test 3: Prueba personalizada
    # await test_with_specific_model()
    
    print("\n✅ Todos los tests completados!\n")


if __name__ == "__main__":
    asyncio.run(main())
