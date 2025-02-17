from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os

class QuoraSearchInput(BaseModel):
    query: str = Field(..., description="Search query for finding relevant Quora discussions")
    num_results: int = Field(default=5, description="Number of results to return")

class QuoraSearchTool(BaseTool):
    name: str = "Quora Search Tool"
    description: str = "Search for relevant discussions and users on Quora"
    args_schema: Type[BaseModel] = QuoraSearchInput

    def _run(self, query: str, num_results: int = 5) -> str:
        # Using Firecrawl for Quora search
        url = "https://api.firecrawl.dev/v1/search"
        headers = {
            "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": f"site:quora.com {query}",
            "limit": num_results,
            "lang": "en",
            "location": "United States",
            "timeout": 60000,
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    results = data.get("data", [])
                    formatted_results = []
                    for idx, result in enumerate(results):
                        formatted_results.append(f"""
                        Result {idx + 1}:
                        Title: {result.get('title')}
                        URL: {result.get('url')}
                        Snippet: {result.get('snippet')}
                        """)
                    return "\n".join(formatted_results)
        except Exception as e:
            return f"Error searching Quora: {str(e)}"
        
        return "No results found"