"""AWS Bedrock Client - Universal client for all Bedrock foundation models."""

import logging
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError

from ..config import settings
from ..models.bedrock_models import get_model, BedrockModel
from ..utils.validators import validate_messages

logger = logging.getLogger(__name__)


class BedrockClient:
    """Universal AWS Bedrock client that works with any Bedrock foundation model."""
    
    def __init__(self):
        """Initialize Bedrock client (single client for all models)."""
        self.region = settings.AWS_REGION
        
        # Initialize boto3 client (reusable for all models)
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        logger.info(f"Bedrock client initialized: region={self.region}")
    
    def _convert_messages_to_bedrock_format(
        self, 
        messages: List[Dict[str, str]],
        supports_system: bool = True
    ) -> tuple:
        """Convert standard messages to Bedrock converse API format.
        
        Args:
            messages: Standard message format
            supports_system: Whether model supports system messages
            
        Returns:
            Tuple of (system_prompt, conversation_messages)
        """
        system_prompt = None
        conversation = []
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                if supports_system:
                    system_prompt = content
                else:
                    # For models that don't support system, prepend to first user message
                    if not conversation:
                        conversation.append({
                            "role": "user",
                            "content": [{"text": f"System: {content}"}]
                        })
                    else:
                        # Prepend to existing first message
                        conversation[0]["content"][0]["text"] = f"System: {content}\n\n{conversation[0]['content'][0]['text']}"
            elif role == "user":
                conversation.append({"role": "user", "content": [{"text": content}]})
            elif role == "assistant":
                conversation.append({"role": "assistant", "content": [{"text": content}]})
        
        return (system_prompt, conversation)
    
    async def generate(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using any Bedrock model.
        
        Args:
            model_name: Model short name (e.g., 'nova-pro', 'claude-3-5-sonnet')
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Standardized response dictionary with content, usage, finish_reason, model
            
        Raises:
            ValueError: If model not found
            Exception: If API call fails
        """
        validate_messages(messages)
        
        # Get model metadata
        model_info = get_model(model_name)
        
        logger.info(
            f"Bedrock API Call | model={model_name} ({model_info.model_id}), "
            f"messages={len(messages)}, temp={temperature}, max_tokens={max_tokens}"
        )
        
        # Convert to Bedrock format
        system_prompt, conversation = self._convert_messages_to_bedrock_format(
            messages, 
            supports_system=model_info.supports_system
        )
        
        try:
            # Prepare converse parameters
            converse_params = {
                "modelId": model_info.model_id,
                "messages": conversation,
                "inferenceConfig": {
                    "temperature": temperature,
                    "maxTokens": min(max_tokens, model_info.max_tokens)  # Respect model limits
                }
            }
            
            # Add system prompt if supported and present
            if system_prompt and model_info.supports_system:
                converse_params["system"] = [{"text": system_prompt}]
            
            # Call Bedrock Converse API
            response = self.client.converse(**converse_params)
            
            # Extract response
            output_message = response["output"]["message"]
            content = output_message["content"][0]["text"]
            
            # Extract usage
            usage = response.get("usage", {})
            input_tokens = usage.get("inputTokens", 0)
            output_tokens = usage.get("outputTokens", 0)
            total_tokens = usage.get("totalTokens", input_tokens + output_tokens)
            
            # Get finish reason
            finish_reason = response.get("stopReason", "stop")
            
            logger.info(
                f"Bedrock response | model={model_name}, tokens={total_tokens}, "
                f"finish_reason={finish_reason}"
            )
            
            return {
                "content": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens
                },
                "finish_reason": finish_reason,
                "model": model_name,
                "model_id": model_info.model_id
            }
            
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(f"Bedrock API error: {error_code} - {error_message}")
            raise Exception(f"Bedrock error ({model_name}): {error_code} - {error_message}")
        
        except Exception as e:
            logger.error(f"Unexpected error calling Bedrock: {str(e)}")
            raise
    
    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a Bedrock model.
        
        Args:
            model_name: Model short name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        model_info = get_model(model_name)
        
        input_cost = (input_tokens / 1000) * model_info.input_cost_per_1k
        output_cost = (output_tokens / 1000) * model_info.output_cost_per_1k
        
        return input_cost + output_cost


# Singleton instance
bedrock_client = BedrockClient()


__all__ = ["BedrockClient", "bedrock_client"]
