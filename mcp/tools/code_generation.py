import requests
import os
import json
import re
from config import (
    GROQ_API_KEY,
    CODE_GENERATION_MODEL,
    CODE_GENERATION_TEMPERATURE,
    CODE_GENERATION_MAX_TOKENS
)

TOOL_NAME = "code_generation"
TOOL_DESCRIPTION = "Generate code snippets and programming solutions using Groq AI with structured output"
TOOL_PARAMETERS = {
    "prompt": "Description of the code to generate",
    "structured_output": "(Optional) Set to 'true' for JSON formatted response with metadata. Default: 'true'"
}

def extract_code_blocks(content: str) -> list:
    """Extract code blocks from markdown-formatted content"""
    # Match code blocks with language specification
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    return [{"language": lang or "unknown", "code": code.strip()} for lang, code in matches]

def execute(params: dict) -> str:
    """Generate code using Groq API with structured output"""
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
        "model": CODE_GENERATION_MODEL,
        "temperature": CODE_GENERATION_TEMPERATURE,
        "max_tokens": CODE_GENERATION_MAX_TOKENS
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        
        content = response_data["choices"][0]["message"]["content"].strip()
        
        if structured_output:
            # Extract code blocks from the response
            code_blocks = extract_code_blocks(content)
            
            # Return structured JSON output
            structured_response = {
                "status": "success",
                "tool": TOOL_NAME,
                "content": content,
                "code_blocks": code_blocks,
                "metadata": {
                    "model": response_data.get("model", CODE_GENERATION_MODEL),
                    "prompt_tokens": response_data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": response_data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": response_data.get("usage", {}).get("total_tokens", 0),
                    "temperature": CODE_GENERATION_TEMPERATURE,
                    "finish_reason": response_data["choices"][0].get("finish_reason", "unknown"),
                    "code_blocks_count": len(code_blocks)
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