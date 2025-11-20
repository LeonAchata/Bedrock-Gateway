"""Test simple del cliente MCP."""

import asyncio
import sys
import io
import os

# Configurar UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar ParaAgente al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'agente'))

from bedrock_client import BedrockGatewayClient

async def test_connection():
    """Test básico de conexión."""
    print("Probando conexión al servidor MCP...")
    
    try:
        async with BedrockGatewayClient() as client:
            print("✅ Conectado exitosamente")
            
            # Listar modelos
            print("\nListando modelos...")
            models = await client.list_models()
            print(f"✅ Modelos disponibles: {len(models)}")
            for model in models[:3]:
                print(f"  - {model['name']}: {model['description'][:50]}...")
            
            # Generar completion
            print("\nGenerando completion...")
            result = await client.generate(
                model="nova-lite",
                messages=[{"role": "user", "content": "Di 'hola' en una palabra"}],
                temperature=0.7,
                max_tokens=50
            )
            
            print(f"\n✅ Respuesta recibida:")
            print(f"   Contenido: {result.get('content', 'N/A')}")
            print(f"   Tokens: {result.get('usage', {}).get('total_tokens', 'N/A')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())
