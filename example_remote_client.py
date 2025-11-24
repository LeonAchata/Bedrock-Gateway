"""Ejemplo de uso del cliente remoto con HTTP/SSE.

Este ejemplo demuestra cómo conectarse al Bedrock Gateway
desplegado en producción usando HTTP/SSE.
"""

import asyncio
import logging
from bedrock_client import BedrockGatewayClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Ejemplo de conexión remota al gateway."""
    
    # Conectar al gateway remoto
    # En producción, cambiar la URL a tu dominio
    async with BedrockGatewayClient(
        gateway_url="http://localhost:8000",  # Cambiar a https://tu-gateway.com
        api_key=None,  # Agregar si implementas autenticación
        timeout=300
    ) as client:
        
        print("\n" + "="*60)
        print("🚀 CONECTADO AL BEDROCK GATEWAY (HTTP/SSE)")
        print("="*60 + "\n")
        
        # 1. Listar modelos disponibles
        print("📋 Modelos disponibles:")
        models = await client.list_models()
        for model in models[:5]:  # Mostrar primeros 5
            print(f"  - {model['name']}: {model['description']}")
        print(f"  ... y {len(models) - 5} modelos más\n")
        
        # 2. Generar completion con Nova Lite (el más económico)
        print("💬 Generando respuesta con Nova Lite...")
        response = await client.generate(
            model="nova-lite",
            messages=[
                {"role": "user", "content": "¿Qué es el protocolo MCP?"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        print(f"\n📝 Respuesta:")
        print(f"{response['content']}\n")
        
        print(f"📊 Métricas:")
        print(f"  - Tokens: {response['usage']['total_tokens']}")
        print(f"  - Costo: ${response['cost_usd']:.6f}")
        print(f"  - Latencia: {response['latency_ms']}ms")
        print(f"  - Cache: {'✅ HIT' if response.get('cached', False) else '❌ MISS'}\n")
        
        # 3. Obtener estadísticas del gateway
        print("📈 Estadísticas del gateway:")
        stats = await client.get_stats()
        metrics = stats.get("metrics", {})
        print(f"  - Requests totales: {metrics.get('total_requests', 0)}")
        print(f"  - Tokens totales: {metrics.get('total_tokens', 0)}")
        print(f"  - Costo total: ${metrics.get('total_cost_usd', 0):.6f}")
        print(f"  - Cache hit rate: {metrics.get('cache_hit_rate_percent', 0):.1f}%\n")
        
        print("="*60)
        print("✅ EJEMPLO COMPLETADO")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
