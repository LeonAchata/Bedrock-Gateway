"""Model routing logic for LLM Gateway - Routes to Bedrock models."""

import time
from typing import Dict, Any
from ..bedrock.bedrock_client import bedrock_client
from ..models.bedrock_models import BEDROCK_MODELS
from ..utils.logger import get_logger
from ..utils.validators import validate_messages, validate_temperature, validate_max_tokens

logger = get_logger(__name__)


class ModelRouter:
    """Routes requests to appropriate LLM providers with caching and metrics."""
    
    def __init__(self, cache_manager=None, metrics_manager=None):
        """Initialize router with optional cache and metrics managers.
        
        Args:
            cache_manager: Cache manager instance
            metrics_manager: Metrics manager instance
        """
        self.cache_manager = cache_manager
        self.metrics_manager = metrics_manager
        logger.info("ModelRouter initialized")
    
    async def route_request(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Route a request to the appropriate LLM provider.
        
        This is the main entry point for all LLM requests. It handles:
        - Validation
        - Cache checking
        - Provider routing
        - Metrics recording
        - Error handling
        
        Args:
            model: Model name to use
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary with response and metadata:
            {
                "content": str,
                "model": str,
                "usage": {
                    "input_tokens": int,
                    "output_tokens": int,
                    "total_tokens": int
                },
                "finish_reason": str,
                "cached": bool,
                "latency_ms": float,
                "estimated_cost_usd": float
            }
            
        Raises:
            ValueError: If validation fails or model not found
            Exception: If generation fails
        """
        start_time = time.time()
        cached = False
        
        try:
            # Validate inputs
            validate_messages(messages)
            validate_temperature(temperature)
            validate_max_tokens(max_tokens)
            
            if model not in BEDROCK_MODELS:
                available = ', '.join(BEDROCK_MODELS.keys())
                raise ValueError(
                    f"Model '{model}' not found. Available models: {available}"
                )
            
            logger.info(
                f"Routing request | model={model}, messages={len(messages)}, "
                f"temp={temperature}, max_tokens={max_tokens}"
            )
            
            # Check cache
            cached_response = None
            if self.cache_manager:
                cached_response = self.cache_manager.get(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            if cached_response:
                cached = True
                response_data = cached_response
                logger.info(f"✓ Cache hit for model={model}")
            else:
                # Call Bedrock with the specified model
                logger.info(f"🔀 Routing to Bedrock model: {model}")
                
                response_data = await bedrock_client.generate(
                    model_name=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                logger.info(
                    f"✓ Provider response: Bedrock - "
                    f"tokens={response_data['usage']['total_tokens']}"
                )
                
                # Cache the response
                if self.cache_manager:
                    self.cache_manager.set(
                        model=model,
                        messages=messages,
                        response=response_data,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            usage = response_data["usage"]
            
            # Estimate cost using Bedrock client
            estimated_cost = bedrock_client.estimate_cost(
                model,
                usage["input_tokens"],
                usage["output_tokens"]
            )
            
            # Record metrics
            if self.metrics_manager:
                self.metrics_manager.record(
                    model=model,
                    tokens=usage["total_tokens"],
                    cost=estimated_cost,
                    latency=latency_ms,
                    cached=cached
                )
            
            logger.info(
                f"Request complete | model={model}, tokens={usage['total_tokens']}, "
                f"cost=${estimated_cost:.4f}, latency={latency_ms:.2f}ms, cached={cached}"
            )
            
            # Return enriched response
            return {
                "content": response_data["content"],
                "model": response_data["model"],
                "usage": usage,
                "finish_reason": response_data["finish_reason"],
                "cached": cached,
                "latency_ms": round(latency_ms, 2),
                "estimated_cost_usd": round(estimated_cost, 6)
            }
            
        except ValueError as e:
            # Validation or model not found error
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Validation error: {str(e)}")
            
            if self.metrics_manager:
                self.metrics_manager.record(
                    model=model,
                    tokens=0,
                    cost=0.0,
                    latency=latency_ms,
                    cached=False,
                    error=True
                )
            
            raise
        
        except Exception as e:
            # Provider or unexpected error
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Error routing request: {str(e)}", exc_info=True)
            
            if self.metrics_manager:
                self.metrics_manager.record(
                    model=model,
                    tokens=0,
                    cost=0.0,
                    latency=latency_ms,
                    cached=False,
                    error=True
                )
            
            raise Exception(f"Failed to generate response: {str(e)}")
