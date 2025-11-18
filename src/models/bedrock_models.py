"""Bedrock Foundation Models Catalog.

This module contains the catalog of all available Bedrock foundation models
with their IDs, pricing, and capabilities.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class BedrockModel:
    """Bedrock model metadata and pricing."""
    
    model_id: str
    name: str
    description: str
    context_window: int
    input_cost_per_1k: float  # USD per 1000 input tokens
    output_cost_per_1k: float  # USD per 1000 output tokens
    supports_system: bool = True
    max_tokens: int = 4096


# Bedrock Foundation Models Catalog
BEDROCK_MODELS: Dict[str, BedrockModel] = {
    # Amazon Nova Models
    "nova-pro": BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        name="Amazon Nova Pro",
        description="Advanced multimodal AI model with superior reasoning",
        context_window=300000,
        input_cost_per_1k=0.0008,
        output_cost_per_1k=0.0032,
        supports_system=True,
        max_tokens=5000
    ),
    "nova-lite": BedrockModel(
        model_id="us.amazon.nova-lite-v1:0",
        name="Amazon Nova Lite",
        description="Fast and cost-effective model for simple tasks",
        context_window=300000,
        input_cost_per_1k=0.00006,
        output_cost_per_1k=0.00024,
        supports_system=True,
        max_tokens=5000
    ),
    "nova-micro": BedrockModel(
        model_id="us.amazon.nova-micro-v1:0",
        name="Amazon Nova Micro",
        description="Ultra-fast model for basic text processing",
        context_window=128000,
        input_cost_per_1k=0.000035,
        output_cost_per_1k=0.00014,
        supports_system=True,
        max_tokens=5000
    ),
    
    # Anthropic Claude Models
    "claude-3-5-sonnet": BedrockModel(
        model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        name="Claude 3.5 Sonnet",
        description="Most intelligent Claude model, best for complex tasks",
        context_window=200000,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        supports_system=True,
        max_tokens=8192
    ),
    "claude-3-5-haiku": BedrockModel(
        model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
        name="Claude 3.5 Haiku",
        description="Fastest Claude model, best for speed",
        context_window=200000,
        input_cost_per_1k=0.001,
        output_cost_per_1k=0.005,
        supports_system=True,
        max_tokens=8192
    ),
    "claude-3-opus": BedrockModel(
        model_id="anthropic.claude-3-opus-20240229-v1:0",
        name="Claude 3 Opus",
        description="Most powerful Claude 3 model",
        context_window=200000,
        input_cost_per_1k=0.015,
        output_cost_per_1k=0.075,
        supports_system=True,
        max_tokens=4096
    ),
    "claude-3-sonnet": BedrockModel(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        name="Claude 3 Sonnet",
        description="Balanced Claude 3 model",
        context_window=200000,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        supports_system=True,
        max_tokens=4096
    ),
    "claude-3-haiku": BedrockModel(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        name="Claude 3 Haiku",
        description="Fast and efficient Claude 3 model",
        context_window=200000,
        input_cost_per_1k=0.00025,
        output_cost_per_1k=0.00125,
        supports_system=True,
        max_tokens=4096
    ),
    
    # Meta Llama Models
    "llama-3-3-70b": BedrockModel(
        model_id="us.meta.llama3-3-70b-instruct-v1:0",
        name="Llama 3.3 70B Instruct",
        description="Latest Llama model with 70B parameters",
        context_window=128000,
        input_cost_per_1k=0.00065,
        output_cost_per_1k=0.00065,
        supports_system=False,
        max_tokens=4096
    ),
    "llama-3-2-90b": BedrockModel(
        model_id="us.meta.llama3-2-90b-instruct-v1:0",
        name="Llama 3.2 90B Instruct",
        description="Multimodal Llama model with vision",
        context_window=128000,
        input_cost_per_1k=0.0008,
        output_cost_per_1k=0.0008,
        supports_system=False,
        max_tokens=4096
    ),
    "llama-3-2-11b": BedrockModel(
        model_id="us.meta.llama3-2-11b-instruct-v1:0",
        name="Llama 3.2 11B Instruct",
        description="Small multimodal Llama model",
        context_window=128000,
        input_cost_per_1k=0.00016,
        output_cost_per_1k=0.00016,
        supports_system=False,
        max_tokens=4096
    ),
    "llama-3-1-70b": BedrockModel(
        model_id="meta.llama3-1-70b-instruct-v1:0",
        name="Llama 3.1 70B Instruct",
        description="Llama 3.1 with 70B parameters",
        context_window=128000,
        input_cost_per_1k=0.00099,
        output_cost_per_1k=0.00099,
        supports_system=False,
        max_tokens=4096
    ),
    "llama-3-1-8b": BedrockModel(
        model_id="meta.llama3-1-8b-instruct-v1:0",
        name="Llama 3.1 8B Instruct",
        description="Small and efficient Llama model",
        context_window=128000,
        input_cost_per_1k=0.00022,
        output_cost_per_1k=0.00022,
        supports_system=False,
        max_tokens=4096
    ),
    
    # Mistral Models
    "mistral-large-2": BedrockModel(
        model_id="mistral.mistral-large-2407-v1:0",
        name="Mistral Large 2",
        description="Flagship Mistral model with advanced reasoning",
        context_window=128000,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.009,
        supports_system=True,
        max_tokens=8192
    ),
    "mistral-small": BedrockModel(
        model_id="mistral.mistral-small-2402-v1:0",
        name="Mistral Small",
        description="Fast and affordable Mistral model",
        context_window=32000,
        input_cost_per_1k=0.001,
        output_cost_per_1k=0.003,
        supports_system=True,
        max_tokens=8192
    ),
}


def get_model(model_name: str) -> BedrockModel:
    """Get Bedrock model by name.
    
    Args:
        model_name: Short name of the model (e.g., 'nova-pro', 'claude-3-5-sonnet')
        
    Returns:
        BedrockModel instance
        
    Raises:
        ValueError: If model not found
    """
    if model_name not in BEDROCK_MODELS:
        available = ", ".join(BEDROCK_MODELS.keys())
        raise ValueError(f"Model '{model_name}' not found. Available: {available}")
    
    return BEDROCK_MODELS[model_name]


def list_all_models() -> list[Dict[str, Any]]:
    """List all available Bedrock models.
    
    Returns:
        List of model metadata dictionaries
    """
    return [
        {
            "name": name,
            "model_id": model.model_id,
            "description": model.description,
            "context_window": model.context_window,
            "input_cost_per_1k": model.input_cost_per_1k,
            "output_cost_per_1k": model.output_cost_per_1k,
            "supports_system": model.supports_system,
            "max_tokens": model.max_tokens
        }
        for name, model in BEDROCK_MODELS.items()
    ]


__all__ = [
    "BedrockModel",
    "BEDROCK_MODELS",
    "get_model",
    "list_all_models"
]
