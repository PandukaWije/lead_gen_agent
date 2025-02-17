from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
import csv
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CSVWriterInput(BaseModel):
    data: List[Dict] = Field(..., description="Data to write to CSV")
    company_description: str = Field(..., description="Company description for filename")

class CSVWriterTool(BaseTool):
    name: str = "CSV Writer Tool"
    description: str = "Write lead data to a CSV file"
    args_schema: Type[BaseModel] = CSVWriterInput

    def _run(self, data: List[Dict], company_description: str) -> str:
        logger.info(f"Starting CSV write operation for {len(data)} records")
        
        try:
            # Create output directory if it doesn't exist
            output_dir = "lead_generation_output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/leads_{company_description.replace(' ', '_')}_{timestamp}.csv"
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            logger.info(f"Successfully wrote data to CSV: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error writing to CSV: {str(e)}", exc_info=True)
            raise Exception(f"Failed to write CSV: {str(e)}")