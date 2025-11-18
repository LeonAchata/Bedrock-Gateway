"""Validation utilities for LLM Gateway."""

from typing import List, Dict, Any


def validate_messages(messages: List[Dict[str, str]]) -> None:
    """Validate message format for LLM requests.
    
    Args:
        messages: List of message dictionaries
        
    Raises:
        ValueError: If messages format is invalid
    """
    if not messages:
        raise ValueError("Messages list cannot be empty")
    
    if not isinstance(messages, list):
        raise ValueError("Messages must be a list")
    
    valid_roles = {"system", "user", "assistant"}
    
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            raise ValueError(f"Message {i} must be a dictionary")
        
        if "role" not in msg or "content" not in msg:
            raise ValueError(f"Message {i} must have 'role' and 'content' keys")
        
        if msg["role"] not in valid_roles:
            raise ValueError(
                f"Message {i} has invalid role '{msg['role']}'. "
                f"Must be one of: {valid_roles}"
            )
        
        if not isinstance(msg["content"], str):
            raise ValueError(f"Message {i} content must be a string")
        
        if not msg["content"].strip():
            raise ValueError(f"Message {i} content cannot be empty")


def validate_temperature(temperature: float) -> None:
    """Validate temperature parameter.
    
    Args:
        temperature: Temperature value to validate
        
    Raises:
        ValueError: If temperature is invalid
    """
    if not isinstance(temperature, (int, float)):
        raise ValueError("Temperature must be a number")
    
    if not 0.0 <= temperature <= 2.0:
        raise ValueError("Temperature must be between 0.0 and 2.0")


def validate_max_tokens(max_tokens: int) -> None:
    """Validate max_tokens parameter.
    
    Args:
        max_tokens: Max tokens value to validate
        
    Raises:
        ValueError: If max_tokens is invalid
    """
    if not isinstance(max_tokens, int):
        raise ValueError("Max tokens must be an integer")
    
    if max_tokens <= 0:
        raise ValueError("Max tokens must be greater than 0")
    
    if max_tokens > 100000:  # Reasonable upper limit
        raise ValueError("Max tokens cannot exceed 100000")


def validate_model_name(model_name: str, available_models: List[str]) -> None:
    """Validate model name against available models.
    
    Args:
        model_name: Model name to validate
        available_models: List of available model names
        
    Raises:
        ValueError: If model name is invalid
    """
    if not isinstance(model_name, str):
        raise ValueError("Model name must be a string")
    
    if not model_name.strip():
        raise ValueError("Model name cannot be empty")
    
    if model_name not in available_models:
        available = ", ".join(available_models)
        raise ValueError(
            f"Model '{model_name}' not found. Available models: {available}"
        )
