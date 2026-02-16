# AI API Integration Strategy

## Overview
VibeBench integrates with multiple AI-based coding assistants to generate code for benchmarking. This document specifies the API integration approach, authentication mechanisms, rate limiting strategies, and version management.

## Supported AI Models

### 1. GitHub Copilot
**API Endpoint:** GitHub Copilot Chat API (via Visual Studio Code Extension Host)  
**Authentication:** GitHub OAuth + Device Flow or Personal Access Token  
**Documentation:** https://docs.github.com/en/copilot/overview-of-github-copilot

**Integration Options:**
- **Option A (Recommended):** Use VS Code Extension Protocol
  - Leverage existing Copilot installation in VS Code
  - No separate API key management required
  - Limitation: Requires VS Code IDE to be running
  - Implementation: IPC communication with VS Code process

- **Option B:** GitHub Copilot Business API (When Available)
  - Direct API access for enterprise deployments
  - Managed authentication via OAuth
  - Rate limiting: 300 requests per hour (subject to plan)
  - Cost: Covered by GitHub Copilot Business subscription

**Model Versions to Track:**
- Version identifier format: `copilot-vX.Y.Z-<date>`
- Example: `copilot-v1.50.0-2024-12-15`
- Store in metadata for reproducibility

### 2. OpenAI (GPT-3.5 Turbo, GPT-4, GPT-4 Turbo)
**API Endpoint:** `https://api.openai.com/v1/chat/completions`  
**Authentication:** Bearer token (API key)  
**Documentation:** https://platform.openai.com/docs

**Configuration:**
```python
{
  "model": "gpt-4-turbo-preview",
  "api_key": "${OPENAI_API_KEY}",  # From environment variables
  "base_url": "https://api.openai.com/v1",
  "timeout": 60,  # seconds per request
  "max_retries": 3,
  "rate_limit": {
    "requests_per_minute": 3500,  # For Free/Pay-as-you-go users
    "tokens_per_minute": 90000
  }
}
```

**Model Versions:**
- GPT-3.5 Turbo: `gpt-3.5-turbo-0125` (specific snapshots only)
- GPT-4: `gpt-4-0613` or `gpt-4-1106-preview`
- GPT-4 Turbo: `gpt-4-turbo-preview`
- Track cutoff dates: GPT-4 Turbo has knowledge cutoff of April 2024

**Pricing:** 
- GPT-3.5 Turbo: $0.50 per 1M input tokens, $1.50 per 1M output tokens
- GPT-4: $10 per 1M input tokens, $30 per 1M output tokens
- GPT-4 Turbo: $10 per 1M input tokens, $30 per 1M output tokens
- Track costs per benchmark run for ROI analysis

### 3. Anthropic (Claude 3 Opus, Sonnet, Haiku)
**API Endpoint:** `https://api.anthropic.com/v1/messages`  
**Authentication:** Bearer token (API key)  
**Documentation:** https://docs.anthropic.com/

**Configuration:**
```python
{
  "model": "claude-3-opus-20240229",
  "api_key": "${ANTHROPIC_API_KEY}",
  "base_url": "https://api.anthropic.com/v1",
  "timeout": 120,  # Anthropic has longer processing times
  "max_retries": 3,
  "rate_limit": {
    "requests_per_minute": 50,  # Base tier
    "tokens_per_minute": 40000
  }
}
```

**Model Versions:**
- Claude 3 Opus: `claude-3-opus-20240229` (latest)
- Claude 3 Sonnet: `claude-3-sonnet-20240229`
- Claude 3 Haiku: `claude-3-haiku-20240307`
- Store version ID and release date

**Pricing:**
- Opus: $15 per 1M input tokens, $75 per 1M output tokens
- Sonnet: $3 per 1M input tokens, $15 per 1M output tokens
- Haiku: $0.80 per 1M input tokens, $4 per 1M output tokens

### 4. Google (Gemini Pro, Gemini Pro Vision)
**API Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models`  
**Authentication:** API key (free tier) or OAuth (enterprise)  
**Documentation:** https://ai.google.dev/docs

**Configuration:**
```python
{
  "model": "gemini-pro",
  "api_key": "${GOOGLE_API_KEY}",
  "base_url": "https://generativelanguage.googleapis.com/v1beta",
  "timeout": 60,
  "max_retries": 3,
  "rate_limit": {
    "requests_per_minute": 60,  # Free tier
    "tokens_per_minute": 1000000
  }
}
```

**Model Versions:**
- Gemini Pro: `gemini-pro`
- Gemini Pro Vision: `gemini-pro-vision`
- Store model version from API response header

**Pricing:**
- Free tier: 60 requests per minute
- Paid: $0.0025 per 1K input tokens, $0.0075 per 1K output tokens

## API Request/Response Contract

### Standard VibeBench Request Format
```python
{
  "ai_model": "gpt-4-turbo",
  "task_id": "B",  # Task identifier (A-H)
  "language": "python",  # Programming language
  "temperature": 0.7,  # Determinism control (0.0-1.0)
  "max_tokens": 2048,
  "prompt": "Your standardized prompt for this task...",
  "system_message": "You are an expert Python developer...",
  "timeout": 60,  # seconds
  "retry_config": {
    "max_attempts": 3,
    "backoff_strategy": "exponential",
    "backoff_factor": 2
  }
}
```

### Standard VibeBench Response Format
```python
{
  "success": True,
  "ai_model": "gpt-4-turbo",
  "model_version": "gpt-4-turbo-2024-04-09",
  "code": "import json\n...",
  "metadata": {
    "tokens_used": {"input": 245, "output": 512},
    "cost": 0.0085,
    "api_provider": "openai",
    "timestamp": "2024-02-16T14:30:22Z",
    "latency_ms": 1250,
    "attempts": 1
  },
  "errors": []
}
```

## Rate Limiting Strategy

### Burst Handling
```python
class RateLimiter:
    def __init__(self, requests_per_minute, tokens_per_minute):
        self.rpm_limit = requests_per_minute
        self.tpm_limit = tokens_per_minute
        self.token_bucket = TokenBucket(capacity=tpm_limit)
        self.request_queue = deque()
    
    def acquire(self, token_count, timeout=60):
        """Acquire rate limit slot with exponential backoff"""
        retry_count = 0
        while retry_count < 5:
            try:
                self.token_bucket.consume(token_count)
                return True
            except RateLimitExceeded:
                wait_time = (2 ** retry_count) + random(0, 1)
                time.sleep(min(wait_time, timeout))
                retry_count += 1
        raise RateLimitExceeded(f"Exceeded after {retry_count} retries")
```

### Per-Provider Limits
- **OpenAI:** Respect both TPM and RPM limits; prioritize TPM
- **Anthropic:** Lower RPM limit requires batching of requests
- **Google:** Free tier very restrictive; queue requests
- **Copilot:** IDE-based, no external rate limits

### Queue Management
- Implement FIFO task queue for requests exceeding rate limits
- Estimated wait times shown to users
- Configurable priority (round-robin, priority-based, FIFO)

## Authentication & Secret Management

### Environment Variable Configuration
```bash
# .env file (NEVER commit to version control)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GITHUB_COPILOT_TOKEN=gho_...
VIBEBENCH_ENV=production
```

### Vault Integration (Enterprise)
```python
# For production deployments
from hvac import Client

vault_client = Client(url='https://vault.company.com', token=os.getenv('VAULT_TOKEN'))
api_keys = vault_client.secrets.kv.read_secret_version(path='secret/vibebench/api-keys')
openai_key = api_keys['data']['data']['openai_api_key']
```

### Key Rotation Policy
- Rotate API keys quarterly (or per organization policy)
- No keys hardcoded in source code
- Monitor for accidental key commits via pre-commit hooks
- Use short-lived tokens where supported (OAuth)

## Version Pinning & Reproducibility

### Model Version Registry
```json
{
  "gpt-4-turbo": {
    "version": "gpt-4-turbo-2024-04-09",
    "api_model_id": "gpt-4-turbo-preview",
    "knowledge_cutoff": "2024-04-09",
    "training_data_until": "2024-04-09",
    "pinned_date": "2024-02-16",
    "available": true
  },
  "claude-3-opus": {
    "version": "claude-3-opus-20240229",
    "knowledge_cutoff": "2024-02-29",
    "pinned_date": "2024-02-16",
    "available": true
  }
}
```

### Reproducibility Guarantees
- Store full model ID and version in experiment metadata
- Use model snapshots (specific version, not "latest")
- Document API changes that affect determinism
- Re-run historical benchmarks with same model versions for comparison

## Error Handling & Fallback Strategies

### Retry Logic
```python
async def call_ai_with_retry(request, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = await ai_client.request(request)
            return response
        except RateLimitError as e:
            wait_time = e.retry_after or (2 ** attempt)
            await asyncio.sleep(wait_time)
        except APIConnectionError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
        except (InvalidRequestError, AuthenticationError) as e:
            # Non-retryable errors
            raise
```

### Fallback Behavior
1. **Rate Limit Hit:** Queue request, retry with backoff
2. **API Down:** Log error, mark AI as temporarily unavailable, continue with others
3. **Authentication Failure:** Alert administrator, pause benchmark runs
4. **Timeout:** Cancel request after configured timeout, log as incomplete

## Cost Tracking & Monitoring

### Cost Aggregation
```python
{
  "benchmark_run_id": "run_20240216_143022",
  "costs": {
    "gpt-4-turbo": {
      "input_tokens": 245,
      "output_tokens": 512,
      "cost_usd": 0.0085,
      "requests": 1
    },
    "claude-3-opus": {
      "input_tokens": 312,
      "output_tokens": 648,
      "cost_usd": 0.0135,
      "requests": 1
    }
  },
  "total_cost_usd": 0.0220,
  "billing_date": "2024-02-16"
}
```

### Monitoring & Alerts
- Cost tracking dashboard showing spend per AI model, per month
- Alert on cost threshold exceeded (configurable)
- Usage analytics: tokens per model, average latency
- Cost forecasting based on historical patterns

## Testing & Validation

### Test Mode (Offline)
- Use cached responses for development/testing
- Store representative outputs from each AI model
- Replay mechanism for debugging

### Staging Environment
- Separate API keys for staging vs. production
- Lower rate limits for testing
- Detailed logging of all API interactions

### Integration Tests
```python
def test_openai_integration():
    """Test OpenAI API connectivity and response format"""
    request = VibeBenchRequest(
        ai_model="gpt-4-turbo",
        task_id="A",
        language="python"
    )
    response = call_ai(request)
    
    assert response.success
    assert response.code is not None
    assert response.metadata.model_version == "gpt-4-turbo-2024-04-09"
    assert response.metadata.cost > 0
```

## Future Expansion

### New Providers to Support
- **Mistral AI:** Open-source models with managed API
- **Hugging Face Inference:** Custom fine-tuned models
- **xAI Grok:** When API becomes available
- **Local LLMs:** Ollama, LLaMA 2, Falcon (on-premises)

### Provider Abstraction Interface
```python
class AIProviderInterface:
    async def generate_code(self, request: VibeBenchRequest) -> VibeBenchResponse:
        pass
    
    def get_rate_limits(self) -> RateLimits:
        pass
    
    def get_model_info(self, model_id: str) -> ModelInfo:
        pass
    
    def is_available(self) -> bool:
        pass
```

All new providers implement this interface for seamless integration.
