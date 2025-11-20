"""Cliente MCP para comunicación con Bedrock Gateway.

Este cliente se conecta al Bedrock Gateway usando el protocolo MCP
sobre stdio, permitiendo a agentes de LangGraph acceder a múltiples
modelos de Bedrock de forma transparente.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# Intentar importar MCP SDK
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP SDK not installed. Run: pip install mcp")

logger = logging.getLogger(__name__)


class BedrockGatewayClient:
    """Cliente para comunicación con Bedrock Gateway vía MCP.
    
    Este cliente maneja la conexión con el gateway y proporciona
    métodos simples para generar completions con cualquier modelo
    de Bedrock.
    
    Uso:
        ```python
        async with BedrockGatewayClient() as client:
            response = await client.generate(
                model="nova-pro",
                messages=[{"role": "user", "content": "Hola"}]
            )
            print(response["content"])
        ```
    """
    
    def __init__(
        self,
        gateway_command: str = "python",
        gateway_args: list[str] = None,
        gateway_env: Dict[str, str] = None,
        gateway_cwd: str = None
    ):
        """Inicializar cliente MCP.
        
        Args:
            gateway_command: Comando para ejecutar el gateway (default: "python")
            gateway_args: Argumentos del comando (default: ["-m", "src.server"])
            gateway_env: Variables de entorno para el gateway (credentials AWS)
            gateway_cwd: Directorio de trabajo para ejecutar el gateway
        """
        if not MCP_AVAILABLE:
            raise ImportError(
                "MCP SDK is required. Install with: pip install mcp"
            )
        
        self.gateway_command = gateway_command
        self.gateway_args = gateway_args or ["-m", "src.server"]
        
        # Cargar variables de entorno del .env si no se especifican
        if gateway_env is None:
            import os
            from dotenv import load_dotenv
            
            # Obtener directorio raíz del proyecto
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            env_path = os.path.join(project_root, '.env')
            
            # Cargar .env
            if os.path.exists(env_path):
                load_dotenv(env_path)
            
            # Obtener credenciales AWS del entorno
            gateway_env = {
                'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID', ''),
                'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
                'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
                'CACHE_ENABLED': os.getenv('CACHE_ENABLED', 'true'),
                'METRICS_ENABLED': os.getenv('METRICS_ENABLED', 'true'),
                'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO')
            }
        
        self.gateway_env = gateway_env
        
        # Si no se especifica cwd, usar el directorio raíz del proyecto
        if gateway_cwd is None:
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.gateway_cwd = os.path.dirname(current_dir)  # Directorio raíz
        else:
            self.gateway_cwd = gateway_cwd
        
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._client_context = None
        
        logger.info(
            f"BedrockGatewayClient initialized - "
            f"Command: {gateway_command} {' '.join(self.gateway_args)}"
        )
    
    async def connect(self):
        """Conectar al Bedrock Gateway."""
        try:
            logger.info("Connecting to Bedrock Gateway...")
            
            # Crear parámetros del servidor
            server_params = StdioServerParameters(
                command=self.gateway_command,
                args=self.gateway_args,
                env={**self.gateway_env, "PYTHONPATH": self.gateway_cwd}
            )
            
            # Cambiar al directorio del proyecto antes de conectar
            import os
            original_cwd = os.getcwd()
            os.chdir(self.gateway_cwd)
            
            try:
                # Conectar al gateway vía stdio
                self._client_context = stdio_client(server_params)
                self._read, self._write = await self._client_context.__aenter__()
                
                # Crear sesión MCP
                self.session = ClientSession(self._read, self._write)
                await self.session.__aenter__()
                
                # Inicializar sesión
                await self.session.initialize()
                
                logger.info("Connected to Bedrock Gateway successfully")
                
                # Obtener lista de modelos disponibles
                models = await self.list_models()
                logger.info(f"Available models: {len(models)}")
            finally:
                # Restaurar directorio original
                os.chdir(original_cwd)
            
        except Exception as e:
            logger.error(f"Failed to connect to gateway: {str(e)}")
            raise ConnectionError(f"Cannot connect to Bedrock Gateway: {str(e)}")
    
    async def disconnect(self):
        """Desconectar del gateway."""
        try:
            logger.info("Disconnecting from Bedrock Gateway...")
            
            if self.session:
                await self.session.__aexit__(None, None, None)
            
            if self._client_context:
                await self._client_context.__aexit__(None, None, None)
            
            logger.info("Disconnected from Bedrock Gateway")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
    
    async def generate(
        self,
        model: str,
        messages: list[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generar completion usando el Bedrock Gateway.
        
        Args:
            model: Nombre del modelo (ej: "nova-pro", "claude-3-5-sonnet")
            messages: Lista de mensajes con formato [{"role": "user", "content": "..."}]
            temperature: Temperatura de muestreo (0.0-2.0)
            max_tokens: Máximo de tokens a generar
            
        Returns:
            Dict con la respuesta:
            {
                "content": str,           # Texto generado
                "model": str,             # Modelo usado
                "usage": {
                    "input_tokens": int,
                    "output_tokens": int,
                    "total_tokens": int
                },
                "cached": bool,           # Si vino del caché
                "latency_ms": float,      # Latencia en ms
                "estimated_cost_usd": float  # Costo estimado
            }
            
        Raises:
            ValueError: Si el modelo no existe o parámetros inválidos
            Exception: Si hay error en la generación
        """
        if not self.session:
            raise ConnectionError("Not connected to gateway. Call connect() first.")
        
        try:
            logger.info(f"Generating with model={model}, messages={len(messages)}")
            
            # Llamar al tool "generate" del gateway
            result = await self.session.call_tool(
                "generate",
                arguments={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            # Extraer contenido de la respuesta MCP
            if result.content and len(result.content) > 0:
                import json
                
                # El contenido puede venir como JSON string o como objeto
                content_text = result.content[0].text
                
                # Debug: imprimir el contenido completo
                print(f"DEBUG - Content type: {type(content_text)}", file=__import__('sys').stderr)
                print(f"DEBUG - Content: {repr(content_text)}", file=__import__('sys').stderr)
                print(f"DEBUG - Content length: {len(content_text) if isinstance(content_text, str) else 'N/A'}", file=__import__('sys').stderr)
                
                # Si ya es un dict, devolverlo directamente
                if isinstance(content_text, dict):
                    response_data = content_text
                else:
                    # Intentar parsear si es string JSON
                    # Limpiar cualquier espacio o caracteres extraños al inicio
                    content_text = content_text.strip()
                    if not content_text:
                        raise Exception("Empty response content from gateway")
                    response_data = json.loads(content_text)
                
                logger.info(
                    f"Generation complete - "
                    f"tokens={response_data['usage']['total_tokens']}, "
                    f"cost=${response_data.get('estimated_cost_usd', response_data.get('cost_usd', 0)):.6f}"
                )
                
                return response_data
            else:
                raise Exception("Empty response from gateway")
                
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise
    
    async def list_models(self) -> list[Dict[str, Any]]:
        """Listar modelos disponibles en el gateway.
        
        Returns:
            Lista de modelos con metadata:
            [
                {
                    "name": "nova-pro",
                    "model_id": "us.amazon.nova-pro-v1:0",
                    "description": "...",
                    "input_cost_per_1k": 0.0008,
                    "output_cost_per_1k": 0.0032,
                    ...
                }
            ]
        """
        if not self.session:
            raise ConnectionError("Not connected to gateway. Call connect() first.")
        
        try:
            result = await self.session.call_tool("list_models", arguments={})
            
            if result.content and len(result.content) > 0:
                import json
                models = json.loads(result.content[0].text)
                return models
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del gateway (métricas y caché).
        
        Returns:
            Dict con métricas y estadísticas del caché
        """
        if not self.session:
            raise ConnectionError("Not connected to gateway. Call connect() first.")
        
        try:
            result = await self.session.call_tool("get_stats", arguments={})
            
            if result.content and len(result.content) > 0:
                import json
                stats = json.loads(result.content[0].text)
                return stats
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()


# Función helper para uso rápido
async def generate_with_bedrock(
    model: str,
    messages: list[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2000,
    gateway_env: Dict[str, str] = None
) -> Dict[str, Any]:
    """Helper para generar completion sin manejar conexión manualmente.
    
    Args:
        model: Nombre del modelo Bedrock
        messages: Mensajes de la conversación
        temperature: Temperatura
        max_tokens: Tokens máximos
        gateway_env: Variables de entorno AWS (opcional)
        
    Returns:
        Respuesta del modelo
        
    Ejemplo:
        ```python
        response = await generate_with_bedrock(
            model="nova-pro",
            messages=[{"role": "user", "content": "Hola"}],
            gateway_env={
                "AWS_ACCESS_KEY_ID": "...",
                "AWS_SECRET_ACCESS_KEY": "...",
            }
        )
        print(response["content"])
        ```
    """
    async with BedrockGatewayClient(gateway_env=gateway_env) as client:
        return await client.generate(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )


__all__ = [
    "BedrockGatewayClient",
    "generate_with_bedrock"
]
