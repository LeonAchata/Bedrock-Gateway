"""FastMCP server for LLM Gateway - MCP interface for external agents.

This server exposes LLM capabilities through the Model Context Protocol (MCP),
allowing external AI workflows and agents to communicate with various LLM providers
(primarily AWS Bedrock) through a standardized interface.
"""

import sys
import io

# Configurar UTF-8 para Windows
if sys.platform == "win32":
    # Asegurar que stdout use UTF-8 para el protocolo MCP
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stdin, 'buffer'):
        sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

from typing import List, Dict, Any
from fastmcp import FastMCP

from .config import settings
from .mcp.tools import (
    generate_completion,
    list_available_models,
    get_gateway_stats
)
from .utils.logger import setup_logger
from .models.bedrock_models import BEDROCK_MODELS

# Configure logging
logger = setup_logger("llm-gateway", level=settings.LOG_LEVEL)

# Initialize FastMCP server
mcp = FastMCP(
    "LLM Gateway",
    dependencies=["boto3", "botocore", "cachetools"]
)


@mcp.tool()
async def generate(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """Generate LLM completion - Main entry point for all agents.
    
    This is the primary tool that external workflows/agents use to communicate
    with the LLM Gateway. It handles routing to different Bedrock foundation models
    and returns standardized responses with metrics.
    
    Args:
        model: Bedrock model name (e.g., 'nova-pro', 'claude-3-5-sonnet', 'llama-3-3-70b')
        messages: List of conversation messages with 'role' and 'content'
                  Example: [{"role": "user", "content": "Hello!"}]
        temperature: Sampling temperature for randomness (0.0-2.0, default: 0.7)
        max_tokens: Maximum tokens to generate (default: 2000)
    
    Returns:
        Dictionary with generated content and metadata including usage, cost, latency
    
    Example:
        ```python
        response = await generate(
            model="nova-pro",
            messages=[{"role": "user", "content": "What is AI?"}],
            temperature=0.7,
            max_tokens=500
        )
        print(response["content"])
        ```
    """
    logger.info(f"MCP Tool: generate called | model={model}, messages={len(messages)}")
    
    result = await generate_completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    logger.info(f"MCP Tool: generate success | tokens={result['usage']['total_tokens']}")
    return result


@mcp.tool()
async def list_models() -> List[Dict[str, Any]]:
    """List all available Bedrock foundation models and their metadata.
    
    Returns information about all Bedrock models registered in the gateway,
    including their full model IDs, pricing, capabilities, and descriptions.
    
    Returns:
        List of model metadata dictionaries
    
    Example:
        ```python
        models = await list_models()
        for model in models:
            print(f"{model['name']}: {model['description']}")
            print(f"  Input: ${model['input_cost_per_1k']}/1K tokens")
            print(f"  Output: ${model['output_cost_per_1k']}/1K tokens")
        ```
    """
    logger.info("MCP Tool: list_models called")
    
    models = list_available_models()
    
    logger.info(f"MCP Tool: list_models success | count={len(models)}")
    return models


@mcp.tool()
async def get_stats() -> Dict[str, Any]:
    """Get current gateway statistics including metrics and cache info.
    
    Useful for monitoring the gateway's performance, costs, and cache efficiency.
    
    Returns:
        Dictionary with metrics and cache statistics
    
    Example:
        ```python
        stats = await get_stats()
        print(f"Total cost: ${stats['metrics']['total_cost_usd']}")
        print(f"Cache hit rate: {stats['metrics']['cache_hit_rate_percent']}%")
        ```
    """
    logger.info("MCP Tool: get_stats called")
    
    stats = get_gateway_stats()
    
    logger.info("MCP Tool: get_stats success")
    return stats


# Startup event
def run_server():
    """Run the MCP server.
    
    This function initializes and starts the FastMCP server, making it
    available for connections from MCP clients (agents/workflows).
    """
    logger.info("=" * 60)
    logger.info("LLM Gateway (MCP) starting up...")
    logger.info(f"Cache enabled: {settings.CACHE_ENABLED}")
    logger.info(f"Metrics enabled: {settings.METRICS_ENABLED}")
    logger.info(f"Available Bedrock models: {len(BEDROCK_MODELS)}")
    logger.info(f"Registered tools: generate, list_models, get_stats")
    logger.info("=" * 60)
    
    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    run_server()
