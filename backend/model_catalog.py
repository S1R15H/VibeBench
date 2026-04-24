from typing import Any


OLLAMA_CLOUD_MODELS: list[dict[str, Any]] = [
    {
        "key": "qwen3-coder",
        "name": "Qwen 3 Coder 480B (Cloud)",
        "model_id": "qwen3-coder:480b",
        "provider": "Ollama Cloud",
        "pricing_prompt": 0.0,
        "pricing_completion": 0.0,
        "description": "FREE. Ultra-large specialized coding model for complex tasks.",
    },
    {
        "key": "mistral-large",
        "name": "Mistral Large 3 675B (Cloud)",
        "model_id": "mistral-large-3:675b",
        "provider": "Ollama Cloud",
        "pricing_prompt": 0.0,
        "pricing_completion": 0.0,
        "description": "FREE. Flagship model from Mistral, high reasoning and precision.",
    },
    {
        "key": "gpt-oss",
        "name": "GPT-OSS 120B (Cloud)",
        "model_id": "gpt-oss:120b",
        "provider": "Ollama Cloud",
        "pricing_prompt": 0.0,
        "pricing_completion": 0.0,
        "description": "FREE. Balanced high-performance open-source model.",
    },
    {
        "key": "gemma3",
        "name": "Gemma 3 27B (Cloud)",
        "model_id": "gemma3:27b",
        "provider": "Ollama Cloud",
        "pricing_prompt": 0.0,
        "pricing_completion": 0.0,
        "description": "FREE. Latest model from Google, optimized for speed and quality.",
    },
    {
        "key": "devstral",
        "name": "Devstral 2 123B (Cloud)",
        "model_id": "devstral-2:123b",
        "provider": "Ollama Cloud",
        "pricing_prompt": 0.0,
        "pricing_completion": 0.0,
        "description": "FREE. Specialized model for software engineering and documentation.",
    },
]


def get_supported_models() -> list[dict[str, Any]]:
    return [dict(model) for model in OLLAMA_CLOUD_MODELS]


def get_model_config(model_key: str) -> dict[str, Any]:
    for model in OLLAMA_CLOUD_MODELS:
        if model["key"] == model_key:
            return dict(model)
    raise KeyError(f"Unknown model key: {model_key}")


def is_supported_model(model_key: str) -> bool:
    return any(model["key"] == model_key for model in OLLAMA_CLOUD_MODELS)
