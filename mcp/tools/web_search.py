import requests
import json
from ddgs import DDGS
from typing import List, Dict
from config import WEB_SEARCH_MAX_RESULTS

TOOL_NAME = "web_search"
TOOL_DESCRIPTION = "Search the web for current information using Live Web Search feature with structured output"
TOOL_PARAMETERS = {
    "query": "The search query",
    "structured_output": "Set to 'true' for JSON formatted response with metadata. Default: 'true'"
}

def execute(params: dict) -> str:
    query = params.get("query", "")
    structured_output = params.get("structured_output", "true").lower() == "true"
    
    if not query:
        raise ValueError("'query' parameter is required")
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=WEB_SEARCH_MAX_RESULTS))
            
            if structured_output:
                structured_results = []
                for i, r in enumerate(results, 1):
                    structured_results.append({
                        "rank": i,
                        "title": r.get('title', 'No title'),
                        "description": r.get('body', 'No description'),
                        "url": r.get('href', 'No URL'),
                        "source": r.get('source', 'Unknown')
                    })
                
                structured_response = {
                    "status": "success",
                    "tool": TOOL_NAME,
                    "query": query,
                    "results": structured_results,
                    "metadata": {
                        "total_results": len(structured_results),
                        "max_results": WEB_SEARCH_MAX_RESULTS,
                        "search_engine": "DuckDuckGo"
                    }
                }
                return json.dumps(structured_response, indent=2)
            else:
                # Return plain text format
                formatted_results = []
                for i, r in enumerate(results, 1):
                    formatted_results.append(
                        f"{i}. {r.get('title', 'No title')}\n"
                        f"   {r.get('body', 'No description')}\n"
                        f"   URL: {r.get('href', 'No URL')}"
                    )
                return "\n\n".join(formatted_results)
                
    except Exception as e:
        error_response = {
            "status": "error",
            "tool": TOOL_NAME,
            "error": str(e),
            "error_type": type(e).__name__,
            "query": query
        }
        if structured_output:
            return json.dumps(error_response, indent=2)
        else:
            raise RuntimeError(f"DuckDuckGo search error: {str(e)}")