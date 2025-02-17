# tasks/tasks.py
from crewai import Task
from typing import List
from agents.researcher_agent import ResearcherAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.writer_agent import WriterAgent

class LeadGenTasks:
    @staticmethod
    def research_task(target_description: str) -> Task:
        return Task(
            description=f"""
            Research potential leads who are interested in or looking for 
            {target_description}. Search across both Quora and other platforms 
            using Exa. Focus on finding people who:
            1. Are actively discussing the topic
            2. Have asked questions about solutions
            3. Show clear interest or need
            
            Provide detailed information about each potential lead including:
            - Their role/background
            - Their specific needs or interests
            - Platform where they were found
            - Level of engagement with the topic
            """,
            expected_output="""A list of potential leads in JSON format with the following structure:
            [
                {
                    "Website URL": "URL where found",
                    "Username": "User's name or handle",
                    "Bio": "User's bio or description",
                    "Post Type": "question or answer",
                    "Timestamp": "When the interaction occurred",
                    "Upvotes": "Number of upvotes",
                    "Links": "Any relevant links"
                }
            ]
            """,
            agent=ResearcherAgent.create()
        )

    @staticmethod
    def analyze_task() -> Task:
        return Task(
            description="""
            Analyze the gathered leads and add qualification data to each record.
            For each lead, analyze:
            1. Likelihood to convert
            2. Urgency of their need
            3. Decision-making authority
            4. Engagement level
            
            Add these fields to each lead record while maintaining the original data.
            """,
            expected_output="""A JSON array of leads with added qualification data:
            [
                {
                    // Original fields remain
                    "Website URL": "...",
                    "Username": "...",
                    // New qualification fields
                    "Qualification Score": "1-10",
                    "Priority": "High/Medium/Low",
                    "Notes": "Qualification notes",
                    "Recommended Approach": "Outreach strategy"
                }
            ]
            """,
            agent=AnalyzerAgent.create()
        )

    @staticmethod
    def document_task() -> Task:
        return Task(
            description="""
            Save the qualified lead data in two formats:
            1. Required: CSV file with all lead data
            2. Optional: Google Sheet (if possible)
            
            The data should maintain all fields from the analysis phase.
            Handle any errors gracefully and ensure the CSV is always created
            even if the Google Sheet export fails.
            """,
            expected_output="""A JSON object containing:
            {
                "csv_file": "Path to the created CSV file",
                "google_sheet_url": "URL of the Google Sheet (or null if failed)",
                "total_leads": "Number of leads processed",
                "status": "Success message or error details"
            }
            """,
            agent=WriterAgent.create()
        )