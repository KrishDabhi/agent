import requests
import os
from config import (
    GROQ_API_KEY,
    CODE_GENERATION_MODEL,
    CODE_GENERATION_TEMPERATURE,
    CODE_GENERATION_MAX_TOKENS
)

TOOL_NAME = "code_generation"
TOOL_DESCRIPTION = "Generate code snippets and programming solutions using Groq AI"
TOOL_PARAMETERS = {
    "prompt": "Description of the code to generate"
}

def execute(params: dict) -> str:
    """Generate code using Groq API"""
    prompt = params.get("prompt", "")
    
    if not prompt:
        raise ValueError("'prompt' parameter is required")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "model": CODE_GENERATION_MODEL,
        "temperature": CODE_GENERATION_TEMPERATURE,
        "max_tokens": CODE_GENERATION_MAX_TOKENS
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Groq API error: {str(e)}")