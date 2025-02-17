from crewai import Agent

class AnalyzerAgent:
    @staticmethod
    def create() -> Agent:
        return Agent(
            role='Lead Quality Analyzer',
            goal='Analyze and qualify leads based on their engagement and needs',
            backstory="""You are an experienced lead qualifier who can identify 
            the most promising prospects. You understand buyer intent signals and 
            can prioritize leads based on their likelihood to convert.""",
            verbose=True,
            allow_delegation=True
        )