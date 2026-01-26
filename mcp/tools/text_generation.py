import requests
import os
from config import (
    GROQ_API_KEY,  # Changed from GROK to GROQ
    TEXT_GENERATION_MODEL,
    TEXT_GENERATION_TEMPERATURE,
    TEXT_GENERATION_MAX_TOKENS
)

TOOL_NAME = "text_generation"
TOOL_DESCRIPTION = "Generate detailed text explanations and answers using Grok AI"
TOOL_PARAMETERS = {
    "prompt": "The text prompt or question to generate a response for"
}


def execute(params: dict) -> str:
    """Generate detailed explanations using Grok API"""
    prompt = params.get("prompt", "")
    
    if not prompt:
        raise ValueError("'prompt' parameter is required")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"  # Fixed: using GROQ_API_KEY
    }
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": TEXT_GENERATION_MODEL,
        "temperature": TEXT_GENERATION_TEMPERATURE,
        "max_tokens": TEXT_GENERATION_MAX_TOKENS
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Grok API error: {str(e)}")