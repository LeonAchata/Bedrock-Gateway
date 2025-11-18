"""MCP Tools for LLM Gateway - Interface for external agents."""

from typing import List, Dict, Any
from ..core.router import ModelRouter
from ..core.cache import cache_manager
from ..core.metrics import metrics_manager
from ..models.bedrock_models import BEDROCK_MODELS, list_all_models
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Initialize router with cache and metrics
router = ModelRouter(
    cache_manager=cache_manager,
    metrics_manager=metrics_manager
)


async def generate_completion(
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
        model: Bedrock model identifier (e.g., 'nova-pro', 'claude-3-5-sonnet', 'llama-3-3-70b')
        messages: List of conversation messages with 'role' and 'content'
                  Example: [{"role": "user", "content": "Hello!"}]
        temperature: Sampling temperature for randomness (0.0-2.0, default: 0.7)
        max_tokens: Maximum tokens to generate (default: 2000)
    
    Returns:
        Dictionary with generated content and metadata:
        {
            "content": "Generated text response",
            "model": "nova-pro",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 50,
                "total_tokens": 60
            },
            "finish_reason": "stop",
            "cached": false,
            "latency_ms": 1234.56,
            "estimated_cost_usd": 0.001234
        }
    
    Raises:
        ValueError: If parameters are invalid or model not found
        Exception: If generation fails
    
    Example usage from agent:
        ```python
        response = await generate_completion(
            model="nova-pro",  # or "claude-3-5-sonnet", "llama-3-3-70b", etc.
            messages=[
                {"role": "user", "content": "What is AI?"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        print(response["content"])
        ```
    """
    logger.info(
        f"MCP Tool called: generate_completion | model={model}, "
        f"messages={len(messages)}, temp={temperature}, max_tokens={max_tokens}"
    )
    
    try:
        result = await router.route_request(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"MCP Tool success | model={model}, tokens={result['usage']['total_tokens']}")
        return result
        
    except Exception as e:
        logger.error(f"MCP Tool error: {str(e)}")
        raise


def list_available_models() -> List[Dict[str, Any]]:
    """List all available Bedrock foundation models and their metadata.
    
    Returns information about all Bedrock models registered in the gateway,
    including their full model IDs, pricing, capabilities, and descriptions.
    
    Returns:
        List of model metadata dictionaries:
        [
            {
                "name": "nova-pro",
                "model_id": "us.amazon.nova-pro-v1:0",
                "description": "Advanced multimodal AI model with superior reasoning",
                "context_window": 300000,
                "input_cost_per_1k": 0.0008,
                "output_cost_per_1k": 0.0032,
                "supports_system": true,
                "max_tokens": 5000
            },
            ...
        ]
    
    Example usage from agent:
        ```python
        models = list_available_models()
        for model in models:
            print(f"{model['name']}: {model['description']}")
            print(f"  Cost: ${model['input_cost_per_1k']}/1K input, ${model['output_cost_per_1k']}/1K output")
        ```
    """
    logger.info("MCP Tool called: list_available_models")
    
    models = list_all_models()
    
    logger.info(f"MCP Tool success | listed {len(models)} Bedrock models")
    return models


def get_gateway_stats() -> Dict[str, Any]:
    """Get current gateway statistics including metrics and cache info.
    
    Useful for monitoring the gateway's performance, costs, and cache efficiency.
    
    Returns:
        Dictionary with metrics and cache statistics:
        {
            "metrics": {
                "total_requests": 100,
                "total_tokens": 50000,
                "total_cost_usd": 1.23,
                "cache_hit_rate_percent": 45.5,
                "average_latency_ms": 1234.5,
                ...
            },
            "cache": {
                "size": 50,
                "max_size": 1000,
                "hit_rate_percent": 45.5
            }
        }
    
    Example usage from agent:
        ```python
        stats = get_gateway_stats()
        print(f"Total cost: ${stats['metrics']['total_cost_usd']}")
        print(f"Cache hit rate: {stats['metrics']['cache_hit_rate_percent']}%")
        ```
    """
    logger.info("MCP Tool called: get_gateway_stats")
    
    try:
        stats = {
            "metrics": metrics_manager.get_stats(),
            "cache": cache_manager.get_stats()
        }
        logger.info("MCP Tool success | retrieved gateway stats")
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise


# Export tools for MCP server registration
__all__ = [
    "generate_completion",
    "list_available_models",
    "get_gateway_stats",
    "router"
]
