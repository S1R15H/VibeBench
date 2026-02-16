# AI API Integration (Research Version)

## Overview
VibeBench benchmarks 4 AI coding assistants:
1. **OpenAI** (GPT-4 Turbo)
2. **Anthropic** (Claude 3 Sonnet)
3. **Google** (Gemini Pro)
4. **GitHub Copilot** (manual copy-paste for now)

For a student project, the focus is simple: "Get API key → Store in .env → Run benchmarks."

## Setup (5 minutes)

### 1. Create `.env` file in project root
```bash
OPENAI_API_KEY=sk-...your-key-here
ANTHROPIC_API_KEY=sk-ant-...your-key-here
GOOGLE_API_KEY=...your-key-here
```

**Never commit `.env` to Git.** Add to `.gitignore`:
```
.env
*.key
```

### 2. Get Free/Trial Credits
- **OpenAI:** Sign up at https://platform.openai.com, get $5 free trial
- **Anthropic:** Free beta access via https://console.anthropic.com
- **Google Gemini:** Free tier at https://ai.google.dev
- **GitHub Copilot:** Use your own subscription or manual copy-paste mode

### 3. Install Dependencies
```bash
pip install openai anthropic google-generativeai python-dotenv
```

### 4. Budget
- **Estimated cost for 12-week project:** $20-50 total
  - 320 benchmarks × 4 models = 1,280 total API calls
  - ~100K tokens used across all calls
  - At current rates: ~$0.03-0.10 per 100K tokens
- **Spend monitoring:** Check your provider dashboards weekly

## Model Specifications

### OpenAI GPT-4 Turbo
- **Endpoint:** https://api.openai.com/v1/chat/completions
- **Model ID:** `gpt-4-turbo-preview`
- **Rate limit:** 3,500 RPM (requests per minute)
- **Cost:** ~$0.01 per task (4 Turbo)
- **Knowledge cutoff:** April 2024

### Anthropic Claude 3 Sonnet
- **Endpoint:** https://api.anthropic.com/v1/messages
- **Model ID:** `claude-3-sonnet-20240229`
- **Rate limit:** 50 RPM (shared across plans)
- **Cost:** ~$0.003 per task
- **Knowledge cutoff:** February 2024

### Google Gemini Pro
- **Endpoint:** https://generativelanguage.googleapis.com/v1beta/models
- **Model ID:** `gemini-pro`
- **Rate limit:** 60 RPM (free tier)
- **Cost:** Free tier available
- **Note:** May change as Google updates Gemini

### GitHub Copilot
- **Integration:** Manual (copy-paste from VS Code)
- **Cost:** Requires Copilot subscription (~$10/month) or use free trial
- **For now:** Students can manually run prompts in Copilot and copy output to VibeBench for recording

## Simple API Client Example

```python
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Example: Call OpenAI
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

response = openai.ChatCompletion.create(
    model='gpt-4-turbo-preview',
    messages=[
        {'role': 'system', 'content': 'You are a helpful coding assistant.'},
        {'role': 'user', 'content': 'Write a Python function that reads a CSV file'}
    ],
    temperature=0.7,
    max_tokens=2048,
    timeout=60
)

print(response['choices'][0]['message']['content'])
```

## Cost Tracking

Create a simple CSV to track spending:

```csv
date,model,api_provider,input_tokens,output_tokens,cost_usd,status
2024-02-16,gpt-4-turbo,openai,245,512,0.0085,success
2024-02-16,claude-sonnet,anthropic,312,648,0.0045,success
2024-02-16,gemini-pro,google,200,400,0.0000,success
```

**Weekly check:** Log into each provider's dashboard and verify spending:
- OpenAI: https://platform.openai.com/account/billing/overview
- Anthropic: https://console.anthropic.com/account/billing
- Google: https://ai.google.dev/dashboard
- **Stop-loss:** If you hit $30 spent, disable API key and debug

## Error Handling (Simple)

```python
try:
    response = call_ai_api(request)
    # Success: save result
except RateLimitError:
    print("Rate limit hit. Waiting 60 seconds...")
    time.sleep(60)
    # Retry
except (ConnectionError, Timeout):
    print("API unavailable. Skipping this model for now.")
    # Continue with next model
except AuthenticationError:
    print("API key invalid. Check .env file.")
    # Exit
```

## Reproducibility

For your research paper, log this for each benchmark run:

```json
{
  "model": "gpt-4-turbo",
  "task": "A",
  "timestamp": "2024-02-16T10:30:00Z",
  "model_version": "gpt-4-turbo-2024-04-09",
  "temperature": 0.7,
  "tokens_used": {"input": 245, "output": 512},
  "cost": 0.0085
}
```

This allows readers to understand exactly which models and versions you used.
