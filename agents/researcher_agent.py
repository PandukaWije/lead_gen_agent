from crewai import Agent
from tools.exa_tools import ExaSearchTool
from tools.quora_tools import QuoraSearchTool

class ResearcherAgent:
    @staticmethod
    def create() -> Agent:
        return Agent(
            role='Lead Research Specialist',
            goal='Find potential leads across multiple platforms based on target criteria',
            backstory="""You are an expert lead researcher with years of experience 
            in identifying high-quality leads. You know how to find people actively 
            discussing or seeking solutions in specific domains.""",
            tools=[ExaSearchTool(), QuoraSearchTool()],
            verbose=True,
            allow_delegation=True
        )