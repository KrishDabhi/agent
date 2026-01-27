"""
Test script to demonstrate structured output from all three tools
"""
import json
from mcp.tools import text_generation, code_generation, web_search

def print_separator(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_text_generation():
    print_separator("TEXT GENERATION - Structured Output")
    
    result = text_generation.execute({
        'prompt': 'Explain what is REST API in 2 sentences',
        'structured_output': 'true'
    })
    
    data = json.loads(result)
    print(json.dumps(data, indent=2))
    
    print("\n--- Key Information ---")
    print(f"Status: {data['status']}")
    print(f"Tool: {data['tool']}")
    print(f"Model: {data['metadata']['model']}")
    print(f"Total Tokens: {data['metadata']['total_tokens']}")
    print(f"Prompt Tokens: {data['metadata']['prompt_tokens']}")
    print(f"Completion Tokens: {data['metadata']['completion_tokens']}")
    print(f"\nContent:\n{data['content']}")

def test_code_generation():
    print_separator("CODE GENERATION - Structured Output")
    
    result = code_generation.execute({
        'prompt': 'Write a simple Python function to reverse a string',
        'structured_output': 'true'
    })
    
    data = json.loads(result)
    
    print("\n--- Key Information ---")
    print(f"Status: {data['status']}")
    print(f"Tool: {data['tool']}")
    print(f"Model: {data['metadata']['model']}")
    print(f"Total Tokens: {data['metadata']['total_tokens']}")
    print(f"Code Blocks Found: {data['metadata']['code_blocks_count']}")
    
    print("\n--- Code Blocks ---")
    for i, block in enumerate(data['code_blocks'], 1):
        print(f"\nBlock {i} ({block['language']}):")
        print(block['code'])

def test_web_search():
    print_separator("WEB SEARCH - Structured Output")
    
    result = web_search.execute({
        'query': 'artificial intelligence 2024',
        'structured_output': 'true'
    })
    
    data = json.loads(result)
    
    print("\n--- Key Information ---")
    print(f"Status: {data['status']}")
    print(f"Tool: {data['tool']}")
    print(f"Query: {data['query']}")
    print(f"Total Results: {data['metadata']['total_results']}")
    print(f"Search Engine: {data['metadata']['search_engine']}")
    
    if data['results']:
        print("\n--- Search Results ---")
        for result in data['results']:
            print(f"\n{result['rank']}. {result['title']}")
            print(f"   {result['description'][:100]}...")
            print(f"   URL: {result['url']}")

def test_plain_text_mode():
    print_separator("PLAIN TEXT MODE (No Structure)")
    
    print("Text Generation (Plain):")
    result = text_generation.execute({
        'prompt': 'What is JSON?',
        'structured_output': 'false'
    })
    print(result)
    
    print("\n\nCode Generation (Plain):")
    result = code_generation.execute({
        'prompt': 'Write hello world in Python',
        'structured_output': 'false'
    })
    print(result)

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# STRUCTURED OUTPUT DEMONSTRATION")
    print("#"*60)
    
    try:
        test_text_generation()
    except Exception as e:
        print(f"Error in text generation: {e}")
    
    try:
        test_code_generation()
    except Exception as e:
        print(f"Error in code generation: {e}")
    
    try:
        test_web_search()
    except Exception as e:
        print(f"Error in web search: {e}")
    
    try:
        test_plain_text_mode()
    except Exception as e:
        print(f"Error in plain text mode: {e}")
    
    print("\n" + "#"*60)
    print("# TEST COMPLETE")
    print("#"*60 + "\n")
