import requests
from duckduckgo_search import DDGS
from typing import List, Dict
from config import WEB_SEARCH_MAX_RESULTS

TOOL_NAME = "web_search"
TOOL_DESCRIPTION = "Search the web for current information using DuckDuckGo"
TOOL_PARAMETERS = {
    "query": "The search query"
}

def execute(params: dict) -> str:
    """Perform web search using DuckDuckGo"""
    query = params.get("query", "")
    
    if not query:
        raise ValueError("'query' parameter is required")
    
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=WEB_SEARCH_MAX_RESULTS)
            
            # Format results as a string
            formatted_results = []
            for i, r in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {r.get('title', 'No title')}\n"
                    f"   {r.get('body', 'No description')}\n"
                    f"   URL: {r.get('href', 'No URL')}"
                )
            
            return "\n\n".join(formatted_results)
    except Exception as e:
        raise RuntimeError(f"DuckDuckGo search error: {str(e)}")