import streamlit as st
import requests
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List
from composio_agno import Action, ComposioToolSet
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'lead_generation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
composio_api_key = os.getenv("COMPOSIO_API_KEY")

class QuoraUserInteractionSchema(BaseModel):
    username: str = Field(description="The username of the user who posted the question or answer")
    bio: str = Field(description="The bio or description of the user")
    post_type: str = Field(description="The type of post, either 'question' or 'answer'")
    timestamp: str = Field(description="When the question or answer was posted")
    upvotes: int = Field(default=0, description="Number of upvotes received")
    links: List[str] = Field(default_factory=list, description="Any links included in the post")

class QuoraPageSchema(BaseModel):
    interactions: List[QuoraUserInteractionSchema] = Field(description="List of all user interactions (questions and answers) on the page")

def search_for_urls(company_description: str, firecrawl_api_key: str, num_links: int) -> List[str]:
    logger.info(f"Starting URL search for company description: {company_description}")
    logger.info(f"Number of requested links: {num_links}")
    
    url = "https://api.firecrawl.dev/v1/search"
    headers = {
        "Authorization": f"Bearer {firecrawl_api_key}",
        "Content-Type": "application/json"
    }
    query1 = f"quora websites where people are looking for {company_description} services"
    payload = {
        "query": query1,
        "limit": num_links,
        "lang": "en",
        "location": "United States",
        "timeout": 60000,
    }
    
    logger.info(f"Sending search request with query: {query1}")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            results = data.get("data", [])
            urls = [result["url"] for result in results]
            logger.info(f"Successfully retrieved {len(urls)} URLs")
            logger.debug(f"Retrieved URLs: {urls}")
            return urls
    
    logger.error(f"Failed to retrieve URLs. Status code: {response.status_code}")
    return []

def extract_user_info_from_urls(urls: List[str], firecrawl_api_key: str) -> List[dict]:
    logger.info(f"Starting user info extraction from {len(urls)} URLs")
    user_info_list = []
    firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
    
    try:
        for url in urls:
            logger.info(f"Processing URL: {url}")
            response = firecrawl_app.extract(
                [url],
                {
                    'prompt': 'Extract all user information including username, bio, post type (question/answer), timestamp, upvotes, and any links from Quora posts. Focus on identifying potential leads who are asking questions or providing answers related to the topic.',
                    'schema': QuoraPageSchema.model_json_schema(),
                }
            )

            logger.debug(f"Firecrawl extraction response for {url}: {json.dumps(response, indent=2)}")
            
            if response.get('success') and response.get('status') == 'completed':
                interactions = response.get('data', {}).get('interactions', [])
                if interactions:
                    logger.info(f"Successfully extracted {len(interactions)} interactions from {url}")
                    user_info_list.append({
                        "website_url": url,
                        "user_info": interactions
                    })
                else:
                    logger.warning(f"No interactions found for URL: {url}")
    except Exception as e:
        logger.error(f"Error extracting user info: {str(e)}", exc_info=True)
    
    logger.info(f"Completed user info extraction. Total successful extractions: {len(user_info_list)}")
    return user_info_list

def format_user_info_to_flattened_json(user_info_list: List[dict]) -> List[dict]:
    logger.info(f"Starting to flatten user info from {len(user_info_list)} sources")
    flattened_data = []
    
    for info in user_info_list:
        website_url = info["website_url"]
        user_info = info["user_info"]
        logger.debug(f"Processing user info from URL: {website_url}")
        
        for interaction in user_info:
            flattened_interaction = {
                "Website URL": website_url,
                "Username": interaction.get("username", ""),
                "Bio": interaction.get("bio", ""),
                "Post Type": interaction.get("post_type", ""),
                "Timestamp": interaction.get("timestamp", ""),
                "Upvotes": interaction.get("upvotes", 0),
                "Links": ", ".join(interaction.get("links", [])),
            }
            flattened_data.append(flattened_interaction)
    
    logger.info(f"Flattening complete. Generated {len(flattened_data)} records")
    logger.debug(f"Flattened data: {json.dumps(flattened_data, indent=2)}")
    return flattened_data

def create_google_sheets_agent(composio_api_key: str, openai_api_key: str) -> Agent:
    logger.info("Creating Google Sheets agent")
    composio_toolset = ComposioToolSet(api_key=composio_api_key)
    google_sheets_tool = composio_toolset.get_tools(actions=[Action.GOOGLESHEETS_SHEET_FROM_JSON])[0]
    
    google_sheets_agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
        tools=[google_sheets_tool],
        show_tool_calls=True,
        description="You are an expert at creating and updating Google Sheets. You will be given user information in JSON format, and you need to write it into a new Google Sheet.",
        markdown=True
    )
    logger.info("Google Sheets agent created successfully")
    return google_sheets_agent

def write_to_csv(flattened_data: List[dict], company_description: str) -> str:
    """Write the flattened data to a CSV file and return the file path."""
    logger.info(f"Starting CSV write operation for {len(flattened_data)} records")
    
    try:
        # Create output directory if it doesn't exist
        output_dir = "lead_generation_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/leads_{company_description.replace(' ', '_')}_{timestamp}.csv"
        
        # Write to CSV
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        
        logger.info(f"Successfully wrote data to CSV: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error writing to CSV: {str(e)}", exc_info=True)
        return None

def write_to_google_sheets(flattened_data: List[dict], composio_api_key: str, openai_api_key: str) -> str:
    """Attempt to write data to Google Sheets (optional)."""
    logger.info(f"Attempting optional Google Sheets write operation for {len(flattened_data)} records")
    
    try:
        google_sheets_agent = create_google_sheets_agent(composio_api_key, openai_api_key)
        
        message = (
            "Create a new Google Sheet with this data. "
            "The sheet should have these columns: Website URL, Username, Bio, Post Type, Timestamp, Upvotes, and Links in the same order as mentioned. "
            "Here's the data in JSON format:\n\n"
            f"{json.dumps(flattened_data)}"
        )
        
        logger.info("Sending data to Google Sheets agent")
        create_sheet_response = google_sheets_agent.run(message)
        
        if "https://docs.google.com/spreadsheets/d/" in create_sheet_response.content:
            google_sheets_link = create_sheet_response.content.split("https://docs.google.com/spreadsheets/d/")[1].split(" ")[0]
            sheet_url = f"https://docs.google.com/spreadsheets/d/{google_sheets_link}"
            logger.info(f"Successfully created Google Sheet: {sheet_url}")
            return sheet_url
    except Exception as e:
        logger.warning(f"Google Sheets export failed (optional): {str(e)}")
        return None
    
    return None

def create_prompt_transformation_agent(openai_api_key: str) -> Agent:
    logger.info("Creating prompt transformation agent")
    agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", api_key=openai_api_key),
        description ="""You are an expert at transforming detailed user queries into concise company descriptions.
Your task is to extract the core business/product focus in 3-4 words.

Examples:
Input: "Generate leads looking for AI-powered customer support chatbots for e-commerce stores."
Output: "AI customer support chatbots for e commerce"

Input: "Find people interested in voice cloning technology for creating audiobooks and podcasts"
Output: "voice cloning technology"

Input: "Looking for users who need automated video editing software with AI capabilities"
Output: "AI video editing software"

Input: "Need to find businesses interested in implementing machine learning solutions for fraud detection"
Output: "ML fraud detection"

Always focus on the core product/service and keep it concise but clear.""",
        markdown=True
    )
    logger.info("Prompt transformation agent created successfully")
    return agent

def main():
    st.title("🎯 AI Lead Generation Agent")
    st.info("This firecrawl powered agent helps you generate leads from Quora by searching for relevant posts and extracting user information.")

    logger.info("Starting lead generation application")
    user_query = st.text_area(
        "Describe what kind of leads you're looking for:",
        placeholder="e.g., Looking for users who need automated video editing software with AI capabilities",
        help="Be specific about the product/service and target audience. The AI will convert this into a focused search query."
    )
    
    num_links = 5

    if st.button("Generate Leads"):
        logger.info(f"Lead generation started with query: {user_query}")
        if not all([firecrawl_api_key, openai_api_key, composio_api_key, user_query]):
            logger.error("Missing required API keys or user query")
            st.error("Please fill in all the API keys and describe what leads you're looking for.")
        else:
            with st.spinner("Processing your query..."):
                transform_agent = create_prompt_transformation_agent(openai_api_key)
                logger.info(f"Transforming user query: {user_query}")
                company_description = transform_agent.run(f"Transform this query into a concise 3-4 word company description: {user_query}")
                logger.info(f"Transformed query: {company_description.content}")
                st.write("🎯 Searching for:", company_description.content)
            
            with st.spinner("Searching for relevant URLs..."):
                urls = search_for_urls(company_description.content, firecrawl_api_key, num_links)
            
            if urls:
                st.subheader("Quora Links Used:")
                for url in urls:
                    st.write(url)
                
                with st.spinner("Extracting user info from URLs..."):
                    user_info_list = extract_user_info_from_urls(urls, firecrawl_api_key)
                
                with st.spinner("Formatting user info..."):
                    flattened_data = format_user_info_to_flattened_json(user_info_list)
                
                # First, write to CSV (required step)
                with st.spinner("Writing to CSV..."):
                    csv_file = write_to_csv(flattened_data, company_description.content)
                
                if csv_file:
                    logger.info("Lead generation process completed successfully")
                    st.success(f"Lead data has been saved to: {csv_file}")
                    
                    # Attempt Google Sheets export (optional step)
                    with st.spinner("Attempting Google Sheets export (optional)..."):
                        google_sheets_link = write_to_google_sheets(flattened_data, composio_api_key, openai_api_key)
                    
                    if google_sheets_link:
                        st.success("Additionally, data was exported to Google Sheets!")
                        st.subheader("Google Sheets Link:")
                        st.markdown(f"[View Google Sheet]({google_sheets_link})")
                    else:
                        st.info("Google Sheets export was not successful (optional step). Your data is still available in the CSV file.")
                else:
                    logger.error("Failed to write data to CSV")
                    st.error("Failed to save the lead data.")
            else:
                logger.warning("No relevant URLs found")
                st.warning("No relevant URLs found.")

    logger.info("Application execution completed")

if __name__ == "__main__":
    main()