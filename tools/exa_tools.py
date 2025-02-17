from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from exa_py import Exa
import os

class ExaSearchInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant content")
    num_results: int = Field(default=5, description="Number of results to return")

class ExaSearchTool(BaseTool):
    name: str = "Exa Search Tool"
    description: str = "Search for relevant content using Exa's semantic search capabilities"
    args_schema: Type[BaseModel] = ExaSearchInput

    def _run(self, query: str, num_results: int = 5) -> str:
        exa = Exa(api_key=os.getenv("EXA_API_KEY"))
        
        response = exa.search_and_contents(
            query,
            type="neural",
            use_autoprompt=True,
            num_results=num_results,
            highlights=True
        )
        
        results = []
        for idx, result in enumerate(response.results):
            results.append(f"""
            Result {idx + 1}:
            Title: {result.title}
            URL: {result.url}
            Highlights: {"".join(result.highlights)}
            """)
            
        return "\n".join(results)