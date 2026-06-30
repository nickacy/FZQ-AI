# FZQ-AI Framework

FZQ-AI is an advanced AI application framework designed for intelligence analysis, news processing, and multi-model orchestration. This framework provides a comprehensive solution for processing and analyzing large volumes of data using various AI models.

## Features

### Core Components
- **LLM Router**: Intelligent routing between multiple AI providers (DeepSeek, OpenAI, Qwen, Kimi, Gemini)
- **Pipeline System**: Modular processing pipelines for various tasks (news, narrative, risk, sentiment analysis)
- **Orchestrator**: Task orchestration with fallback mechanisms and recovery capabilities
- **Unified Interface**: Consistent APIs across different AI providers and processing tasks

### Enhanced Capabilities (New!)
- **Modern Configuration Management**: Dynamic configuration with hot reload capabilities
- **Advanced Error Handling**: Circuit breaker patterns, retry mechanisms, and graceful degradation
- **Performance Optimization**: LRU/TTL caching, concurrent processing, and async optimization
- **Monitoring & Observability**: Comprehensive metrics collection with Prometheus export
- **Security**: Secure credential management and error sanitization

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Layer     │───▶│  Orchestrator   │───▶│  LLM Providers  │
│ (REST/GraphQL)  │    │ (Task Routing)   │    │ (Multi-Model)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌──────────────────┐
                    │   Pipelines      │
                    │ (News, Analysis, │
                    │  Reports, etc.)  │
                    └──────────────────┘
                                │
                                ▼
                    ┌──────────────────┐
                    │   Utilities      │
                    │ (Cache, Logger,  │
                    │  Metrics, etc.)  │
                    └──────────────────┘
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FZQ-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

## Usage

### Basic Example
```python
from fzq_ai.orchestrator.task_orchestrator import TaskOrchestrator

# Initialize orchestrator
orchestrator = TaskOrchestrator()

# Process a request
result = orchestrator.run({
    "query": "Analyze recent developments in AI regulation",
    "task_type": "news_analysis"
})

print(result)
```

### Using Enhanced Features
```python
from fzq_ai.llm.enhanced_cache import llm_response_cache
from fzq_ai.utils.async_manager import AsyncManager
from fzq_ai.metrics.enhanced_metrics import MetricsCollector

# Advanced usage with caching and metrics
async def advanced_example():
    manager = AsyncManager(max_concurrent=10)
    collector = MetricsCollector()
    
    # Check cache first
    cached_result = await llm_response_cache.get("unique_query_id")
    if cached_result:
        return cached_result
    
    # Process with metrics tracking
    start_time = collector.start_timer()
    result = await manager.run_task(process_request())
    
    # Cache result and record metrics
    await llm_response_cache.set("unique_query_id", result, ttl=3600)
    duration = collector.stop_timer_and_record(start_time, "request_processing_time")
    
    return result
```

## Configuration

The framework supports dynamic configuration management:

```python
from fzq_ai.config.modern_config import ConfigManager

config = ConfigManager()
api_key = config.get("DEEPSEEK_API_KEY")
model_settings = config.get("MODEL_SETTINGS")
```

Configuration can be loaded from:
- Environment variables
- Configuration files
- Remote configuration sources (planned)

## Testing

Run the complete test suite:
```bash
python -m pytest tests/ -v
```

Current test coverage: 117 tests passing (including 16 new enhanced feature tests)

## Performance

- Concurrent processing support up to 20 simultaneous operations
- LRU/TTL caching with configurable size and expiration
- Asynchronous operations for optimal performance
- Built-in metrics collection and monitoring

## Contributing

We welcome contributions! Please see our contributing guidelines for more details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

---
*FZQ-AI Framework - Enhanced with Modern AI Capabilities*