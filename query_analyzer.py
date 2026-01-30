from groq import Groq
from config import GROQ_API_KEY
import json


class QueryAnalyzer:
    """Analyzes queries using LLM to determine the best tool"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"
    
    def analyze_query(self, query: str, available_tools: list) -> dict:
        """
        Analyze query and return tool recommendation with confidence
        
        Args:
            query: User's query string
            available_tools: List of available tool names
            
        Returns:
            {
                "recommended_tool": "tool_name",
                "confidence": 95,
                "reasoning": "explanation"
            }
        """
        
        # Create prompt for LLM
        prompt = f"""You are an intelligent query router. Analyze the user's query and determine which tool should handle it.

Available tools:
1. **code_generation** - For writing code, implementing features, building applications, algorithms
2. **web_search** - For real-time info, bookings, prices, news, weather, current events
3. **text_generation** - For explanations, definitions, concepts, tutorials, general knowledge

User Query: "{query}"

Analyze the query and respond in JSON format:
{{
    "recommended_tool": "tool_name",
    "confidence": 85,
    "reasoning": "brief explanation"
}}

Rules:
- If query asks to "write code", "implement", "create code", "build" → code_generation
- If query needs real-time data (flights, weather, news, prices) → web_search
- If query asks to "explain", "what is", "how does" → text_generation
- Confidence should be 0-100
- Only use tools from the available list: {', '.join(available_tools)}

Respond ONLY with valid JSON, no other text."""

        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a query routing expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent routing
                max_tokens=200
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            # Validate result
            if "recommended_tool" not in result:
                raise ValueError("Missing recommended_tool in response")
            
            if result["recommended_tool"] not in available_tools:
                # Fallback to text_generation if invalid tool
                result["recommended_tool"] = "text_generation"
                result["confidence"] = 50
                result["reasoning"] = "Invalid tool recommended, using fallback"
            
            # Ensure confidence is 0-100
            result["confidence"] = max(0, min(100, result.get("confidence", 50)))
            
            return result
            
        except Exception as e:
            # Fallback on error
            print(f"⚠️  Query analyzer error: {e}")
            return {
                "recommended_tool": "text_generation",
                "confidence": 50,
                "reasoning": f"Analysis failed: {str(e)}"
            }
    
    def get_tool_with_confidence(self, query: str, available_tools: list) -> tuple[str, int, str]:
        """
        Convenience method that returns (tool_name, confidence, reasoning)
        """
        result = self.analyze_query(query, available_tools)
        return (
            result["recommended_tool"],
            result["confidence"],
            result.get("reasoning", "")
        )
