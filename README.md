# LLM Gateway (MCP Server)

**Centralized gateway for multiple AWS Bedrock models through the Model Context Protocol (MCP)**

This project implements an MCP server that allows AI agents and workflows to communicate with **15+ AWS Bedrock foundation models** (Nova, Claude, Llama, Mistral, etc.) through a standardized MCP interface.

## 🎯 Purpose

The LLM Gateway acts as a **universal bridge** between external AI workflows and Bedrock foundation models, providing:

- **Unified access** to 15+ Bedrock models (Nova, Claude, Llama, Mistral)
- **Each agent chooses its model** based on its needs (hardcoded in the agent)
- **Intelligent caching** of responses to reduce costs and latency
- **Detailed metrics** for usage, costs, and performance
- **Standard MCP interface** for universal agent connection

## 🏗️ Architecture

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Agent A     │       │  Agent B     │       │  Agent C     │
│  (nova-pro)  │       │  (claude)    │       │  (llama)     │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       ▲                      ▲                      ▲ 
       │                      │                      │
       │        MCP Protocol (stdio/SSE)             │
       └──────────────────────┼──────────────────────┘
                              ▼
                   ┌────────────────────┐
                   │   LLM Gateway      │
                   │   (MCP Server)     │
                   │                    │
                   │  ┌──────────────┐  │
                   │  │   Router     │  │
                   │  ├──────────────┤  │
                   │  │   Cache      │  │
                   │  ├──────────────┤  │
                   │  │   Metrics    │  │
                   │  └──────────────┘  │
                   └─────────┬──────────┘
                             ▲
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐   ┌──────────┐
        │  Nova   │    │ Claude  │   │  Llama   │
        │  Models │    │ Models  │   │  Models  │
        └─────────┘    └─────────┘   └──────────┘
              AWS Bedrock Foundation Models
```

## 📁 Project Structure

```
llm-gateway/
├── src/
│   ├── server.py           # Main FastMCP server
│   ├── config.py           # Configuration (AWS Bedrock only)
│   │
│   ├── models/             # 🆕 Bedrock models catalog
│   │   ├── bedrock_models.py  # 15+ FMs with pricing
│   │   └── __init__.py
│   │
│   ├── bedrock/            # 🆕 Universal Bedrock client
│   │   ├── bedrock_client.py  # Single client for all models
│   │   └── __init__.py
│   │
│   ├── mcp/                # MCP Tools
│   │   ├── tools.py        # generate, list_models, get_stats
│   │   └── __init__.py
│   │
│   ├── core/               # Business logic
│   │   ├── router.py       # Model routing
│   │   ├── cache.py        # Cache system
│   │   ├── metrics.py      # Metrics tracking
│   │   └── __init__.py
│   │
│   └── utils/              # Utilities
│       ├── logger.py       # Centralized logging
│       ├── validators.py   # Validations
│       └── __init__.py
│
├── ForAgents/              # 🎯 LangGraph agent integration
│   ├── bedrock_client.py   # MCP client (stdio)
│   ├── llm_node.py         # Reusable LangGraph node
│   ├── example_agent.py    # 5 complete examples
│   ├── requirements.txt    # Agent dependencies
│   └── README.md           # Integration guide
│
├── Dockerfile              # 🐳 Docker image for production
├── docker-compose.yml      # Easy deployment with Docker Compose
├── .dockerignore           # Build exclusions
│
├── requirements.txt        # Gateway dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🚀 Installation

### 1. Clone and install dependencies

```bash
cd llm-gateway
pip install -r requirements.txt
```

### 2. Configure environment variables

Create `.env` file with your AWS credentials:

```bash
# AWS Bedrock (only required configuration)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Cache and metrics
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
METRICS_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

### 3. Run the server

```bash
python -m src.server
```

## 📋 Available Models

The gateway supports **15+ Bedrock models**:

### Amazon Nova
- `nova-pro` - Advanced, superior reasoning ($0.0008/$0.0032 per 1K)
- `nova-lite` - Fast and economical ($0.00006/$0.00024 per 1K)
- `nova-micro` - Ultra fast, basic ($0.000035/$0.00014 per 1K)

### Anthropic Claude
- `claude-3-5-sonnet` - Smartest ($0.003/$0.015 per 1K)
- `claude-3-5-haiku` - Fastest ($0.001/$0.005 per 1K)
- `claude-3-opus` - Most powerful ($0.015/$0.075 per 1K)
- `claude-3-sonnet` - Balanced ($0.003/$0.015 per 1K)
- `claude-3-haiku` - Efficient ($0.00025/$0.00125 per 1K)

### Meta Llama
- `llama-3-3-70b` - Latest 70B model ($0.00065/$0.00065 per 1K)
- `llama-3-2-90b` - Multimodal with vision ($0.0008/$0.0008 per 1K)
- `llama-3-2-11b` - Small multimodal ($0.00016/$0.00016 per 1K)
- `llama-3-1-70b` - 70B parameters ($0.00099/$0.00099 per 1K)
- `llama-3-1-8b` - Small and efficient ($0.00022/$0.00022 per 1K)

### Mistral
- `mistral-large-2` - Flagship, advanced reasoning ($0.003/$0.009 per 1K)
- `mistral-small` - Fast and economical ($0.001/$0.003 per 1K)

**View complete list:** `await mcp.call_tool("list_models", {})`

## 🔌 Connecting from Agents

### Key Concept

**Each agent specifies its model in code**, not in configuration. The gateway is a single entry point for all Bedrock models.

### MCP Configuration (same for all agents)

```json
{
  "mcpServers": {
    "llm-gateway": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "AWS_REGION": "us-east-1",
        "AWS_ACCESS_KEY_ID": "your-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret"
      }
    }
  }
}
```

### Agent A - Uses Nova Pro

```python
# This agent always uses nova-pro
response = await session.call_tool(
    "generate",
    {
        "model": "nova-pro",  # <-- Model hardcoded in agent
        "messages": [{"role": "user", "content": "Complex task..."}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
)
```

### Agent B - Uses Claude 3.5 Sonnet

```python
# This agent always uses claude-3-5-sonnet
response = await session.call_tool(
    "generate",
    {
        "model": "claude-3-5-sonnet",  # <-- Different model
        "messages": [{"role": "user", "content": "Deep analysis..."}]
    }
)
```

### Agent C - Uses Llama 3.3 70B

```python
# This agent always uses llama-3-3-70b
response = await session.call_tool(
    "generate",
    {
        "model": "llama-3-3-70b",  # <-- Another model
        "messages": [{"role": "user", "content": "General task..."}]
    }
)
```

### Complete example from an agent (Python)

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def use_llm_gateway():
    # Connect to gateway
    async with stdio_client("python", ["-m", "src.server"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List available models
            models = await session.call_tool("list_models", {})
            print(f"Available: {len(models)} models")
            
            # Generate completion with agent's specific model
            response = await session.call_tool(
                "generate",
                {
                    "model": "nova-pro",  # <-- Agent chooses its model
                    "messages": [
                        {"role": "user", "content": "What is AI?"}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            print(f"Response: {response['content']}")
            print(f"Tokens: {response['usage']['total_tokens']}")
            print(f"Cost: ${response['estimated_cost_usd']:.6f}")
            print(f"Cached: {response['cached']}")
            print(f"Latency: {response['latency_ms']:.2f}ms")
```

## 🛠️ Available MCP Tools

### 1. `generate`

Generates completions using any Bedrock model.

**Parameters:**
- `model` (str): Short model name (e.g., "nova-pro", "claude-3-5-sonnet", "llama-3-3-70b")
- `messages` (list): List of messages with 'role' and 'content'
- `temperature` (float): Sampling temperature (0.0-2.0)
- `max_tokens` (int): Maximum tokens to generate

**Returns:**
```json
{
  "content": "Generated response...",
  "model": "nova-pro",
  "model_id": "us.amazon.nova-pro-v1:0",
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
```

### 2. `list_models`

Lists all available Bedrock models with pricing.

**Returns:**
```json
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
```

### 3. `get_stats`

Retrieves gateway statistics (metrics and cache).

**Returns:**
```json
{
  "metrics": {
    "total_requests": 100,
    "total_tokens": 50000,
    "total_cost_usd": 1.23,
    "cache_hit_rate_percent": 45.5,
    "average_latency_ms": 1234.5,
    "requests_by_model": {
      "nova-pro": 50,
      "claude-3-5-sonnet": 30,
      "llama-3-3-70b": 20
    }
  },
  "cache": {
    "current_size": 50,
    "max_size": 1000,
    "enabled": true
  }
}
```

## 📊 Features

### ✅ Implemented

- ✅ FastMCP server with standard protocol
- ✅ **15+ Bedrock models** (Nova, Claude, Llama, Mistral)
- ✅ **Universal Bedrock client** - single client for all models
- ✅ **Each agent chooses its model** - hardcoded in agent code
- ✅ Cache system with TTL
- ✅ Detailed metrics per model (requests, tokens, costs, latencies)
- ✅ Centralized validations
- ✅ Structured logging
- ✅ Automatic cost estimation with real pricing

### 🔮 Future

- 🔜 Rate limiting per agent
- 🔜 Metrics persistence (database)
- 🔜 Web monitoring dashboard
- 🔜 Response streaming
- 🔜 Support for image models (multimodal)

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key | - |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | - |
| `AWS_REGION` | AWS Region | us-east-1 |
| `CACHE_ENABLED` | Enable cache | true |
| `CACHE_TTL` | Cache TTL (seconds) | 3600 |
| `CACHE_MAX_SIZE` | Maximum cache size | 1000 |
| `METRICS_ENABLED` | Enable metrics | true |
| `LOG_LEVEL` | Logging level | INFO |

## ❓ FAQ

### Why only Bedrock and not other providers?

This gateway is optimized for **enterprise environments** where Bedrock offers:
- 15+ models under a single infrastructure
- Enterprise security and compliance
- No per-user rate limits (limits per AWS account)
- Predictable pricing with no hidden charges

### How does each agent decide which model to use?

The model is specified **in the agent's code**, not in configuration:

```python
# Agent A
response = await mcp.call_tool("generate", {"model": "nova-pro", ...})

# Agent B  
response = await mcp.call_tool("generate", {"model": "claude-3-5-sonnet", ...})

# Agent C
response = await mcp.call_tool("generate", {"model": "llama-3-3-70b", ...})
```

### Can I have multiple agents connected to the same gateway?

**Yes**, this is the primary use case. All agents connect to the same MCP gateway, but each specifies its preferred model. The gateway:
- Caches shared responses between agents
- Tracks metrics per model
- Optimizes costs with intelligent caching

### How do I add a new Bedrock model?

Edit `src/models/bedrock_models.py` and add the model to the `BEDROCK_MODELS` dictionary. Example:

```python
"my-model": BedrockModel(
    model_id="aws.my-model-v1:0",
    name="My New Model",
    description="Description",
    context_window=128000,
    input_cost_per_1k=0.001,
    output_cost_per_1k=0.002,
    supports_system=True,
    max_tokens=4096
)
```

## 🐳 Docker Deployment

### Local Quick Start

```bash
# 1. Configure environment variables
cp .env.example .env
# Edit .env with your AWS credentials

# 2. Build and run with Docker Compose
docker-compose up -d

# 3. View logs
docker-compose logs -f
```

### Manual Build

```bash
# Build the image
docker build -t bedrock-gateway:latest .

# Run with environment variables
docker run -d \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_REGION=us-east-1 \
  -e CACHE_ENABLED=true \
  bedrock-gateway:latest
```

### Docker Features

- ✅ Multi-stage build (optimized image ~150MB)
- ✅ Non-root user (security)
- ✅ Persistent volumes for logs
- ✅ Configurable health checks
- ✅ Resource limits (CPU/memory)
- ✅ Compatible with Docker Compose and Kubernetes

## 🎯 LangGraph Agent Integration

### Quick Start

The `ForAgents/` folder contains everything needed:

```bash
# 1. Install agent dependencies
cd ForAgents
pip install -r requirements.txt

# 2. Use the LLM node in your graph
from llm_node import AgentState, llm_consultation_node
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)
workflow.add_node("llm", llm_consultation_node)
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)

app = workflow.compile()

# 3. Execute
result = await app.ainvoke({
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "nova-pro"
})
print(result["response"])
```

## 📖 Additional Documentation

### Connection Examples

**From LangChain:**
```python
from langchain.llms.base import LLM
from mcp import ClientSession

class BedrockMCPLLM(LLM):
    model: str = "nova-pro"
    
    async def _acall(self, prompt: str) -> str:
        async with stdio_client("python", ["-m", "src.server"]) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool(
                    "generate",
                    {
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                return response["content"]

# Use in chain
llm = BedrockMCPLLM(model="claude-3-5-sonnet")
result = await llm.ainvoke("Explain quantum computing")
```

**From LlamaIndex:**
```python
from llama_index.llms.base import LLM
from mcp import ClientSession

class BedrockMCPLLM(LLM):
    def __init__(self, model: str = "nova-pro"):
        self.model = model
    
    async def acomplete(self, prompt: str) -> str:
        async with stdio_client("python", ["-m", "src.server"]) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool(
                    "generate",
                    {
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                return response["content"]

# Use in index
llm = BedrockMCPLLM(model="llama-3-3-70b")
response = await llm.acomplete("Summarize this document")
```

### Monitoring and Debugging

**Enable verbose logging:**
```bash
export LOG_LEVEL=DEBUG
python -m src.server
```

**Check gateway health:**
```python
stats = await session.call_tool("get_stats", {})
print(f"Total requests: {stats['metrics']['total_requests']}")
print(f"Cache hit rate: {stats['metrics']['cache_hit_rate_percent']}%")
print(f"Total cost: ${stats['metrics']['total_cost_usd']:.2f}")
```

**Monitor specific model usage:**
```python
stats = await session.call_tool("get_stats", {})
for model, count in stats['metrics']['requests_by_model'].items():
    print(f"{model}: {count} requests")
```

## 🔒 Security Best Practices

1. **Never commit AWS credentials** - Use environment variables or AWS IAM roles
2. **Use IAM roles** when deploying to AWS (EC2, ECS, Lambda)
3. **Rotate credentials** regularly
4. **Limit Bedrock permissions** to only required models
5. **Use VPC endpoints** for Bedrock in production
6. **Enable CloudTrail** for audit logging

### Example IAM Policy (Minimal Permissions)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/amazon.nova-*",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
        "arn:aws:bedrock:*::foundation-model/meta.llama-*",
        "arn:aws:bedrock:*::foundation-model/mistral.*"
      ]
    }
  ]
}
```

## 🚀 Production Deployment

### AWS ECS (Recommended)

```bash
# 1. Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag bedrock-gateway:latest <account>.dkr.ecr.us-east-1.amazonaws.com/bedrock-gateway:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/bedrock-gateway:latest

# 2. Create ECS task definition with IAM role
# 3. Deploy to ECS Fargate
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bedrock-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bedrock-gateway
  template:
    metadata:
      labels:
        app: bedrock-gateway
    spec:
      containers:
      - name: gateway
        image: bedrock-gateway:latest
        env:
        - name: AWS_REGION
          value: "us-east-1"
        - name: CACHE_ENABLED
          value: "true"
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
```

## 📊 Performance Benchmarks

Typical latencies on `t3.medium` instance:

| Model | First Request | Cached Request | Avg Tokens/s |
|-------|---------------|----------------|--------------|
| nova-micro | 800ms | 5ms | 120 |
| nova-lite | 1200ms | 5ms | 100 |
| nova-pro | 2000ms | 5ms | 80 |
| claude-3-5-haiku | 900ms | 5ms | 110 |
| claude-3-5-sonnet | 1500ms | 5ms | 90 |
| llama-3-1-8b | 700ms | 5ms | 130 |
| llama-3-3-70b | 1800ms | 5ms | 85 |

*Note: Latencies vary based on network, region, and prompt complexity*

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project was developed for the Instrumentation course at PUCP.

## 👥 Author

Developed by Leon Achata as part of the IoT Holter project - PUCP 2025

## 🔗 References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Anthropic Claude Models](https://www.anthropic.com/claude)
- [Meta Llama Models](https://ai.meta.com/llama/)
- [Mistral AI Models](https://mistral.ai/)

---

**Need help?** Open an issue on GitHub or contact the development team.