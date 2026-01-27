import requests
import os
import json
from config import (
    GROQ_API_KEY,
    TEXT_GENERATION_MODEL,
    TEXT_GENERATION_TEMPERATURE,
    TEXT_GENERATION_MAX_TOKENS
)

TOOL_NAME = "text_generation"
TOOL_DESCRIPTION = "Generate detailed text explanations and answers using Groq AI with structured output"
TOOL_PARAMETERS = {
    "prompt": "The text prompt or question to generate a response for",
    "structured_output": "(Optional) Set to 'true' for JSON formatted response with metadata. Default: 'true'"
}


def execute(params: dict) -> str:
    """Generate detailed explanations using Groq API with structured output"""
    prompt = params.get("prompt", "")
    structured_output = params.get("structured_output", "true").lower() == "true"
    
    if not prompt:
        raise ValueError("'prompt' parameter is required")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
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
        response_data = response.json()
        
        content = response_data["choices"][0]["message"]["content"].strip()
        
        if structured_output:
            # Return structured JSON output
            structured_response = {
                "status": "success",
                "tool": TOOL_NAME,
                "content": content,
                "metadata": {
                    "model": response_data.get("model", TEXT_GENERATION_MODEL),
                    "prompt_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response_data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": response_data.get("usage", {}).get("total_tokens", 0),
                    "temperature": TEXT_GENERATION_TEMPERATURE,
                    "finish_reason": response_data["choices"][0].get("finish_reason", "unknown")
                },
                "prompt": prompt
            }
            return json.dumps(structured_response, indent=2)
        else:
            # Return plain text content
            return content
            
    except Exception as e:
        error_response = {
            "status": "error",
            "tool": TOOL_NAME,
            "error": str(e),
            "error_type": type(e).__name__
        }
        if structured_output:
            return json.dumps(error_response, indent=2)
        else:
            raise RuntimeError(f"Groq API error: {str(e)}")