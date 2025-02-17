from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from composio_phidata import Action, ComposioToolSet
import os
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsInput(BaseModel):
    data: List[Dict] = Field(..., description="Data to write to Google Sheets")
    sheet_name: str = Field(default="Leads", description="Name of the sheet")

class GoogleSheetsTool(BaseTool):
    name: str = "Google Sheets Tool"
    description: str = "Create and update Google Sheets with lead information (optional)"
    args_schema: Type[BaseModel] = GoogleSheetsInput

    def _run(self, data: List[Dict], sheet_name: str = "Leads") -> str:
        logger.info(f"Attempting Google Sheets write operation for {len(data)} records")
        try:
            composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
            sheets_tool = composio_toolset.get_tools(
                actions=[Action.GOOGLESHEETS_SHEET_FROM_JSON]
            )[0]
            
            result = sheets_tool.run({
                "data": data,
                "sheet_name": sheet_name
            })
            
            if "https://docs.google.com/spreadsheets" in result:
                sheet_url = result.split("https://docs.google.com/spreadsheets/d/")[1].split(" ")[0]
                full_url = f"https://docs.google.com/spreadsheets/d/{sheet_url}"
                logger.info(f"Successfully created Google Sheet: {full_url}")
                return full_url
            
            logger.warning("Failed to create Google Sheet")
            return "Failed to create Google Sheet"
            
        except Exception as e:
            logger.error(f"Error creating Google Sheet: {str(e)}", exc_info=True)
            return f"Error creating Google Sheet: {str(e)}"