from crewai import Agent
from tools.sheets_tools import GoogleSheetsTool

class WriterAgent:
    @staticmethod
    def create() -> Agent:
        return Agent(
            role='Lead Data Manager',
            goal='Organize and document lead information in a structured format',
            backstory="""You are a detail-oriented data manager who excels at 
            organizing information. You ensure all lead data is properly documented 
            and easily accessible for the sales team.""",
            tools=[GoogleSheetsTool()],
            verbose=True,
            allow_delegation=True
        )