# app.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from crewai import Crew, Process
from tasks.tasks import LeadGenTasks
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    required_keys = [
        "OPENAI_API_KEY",
        "EXA_API_KEY",
        "FIRECRAWL_API_KEY",
        "COMPOSIO_API_KEY"
    ]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    if missing_keys:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_keys)}\n"
            "Please ensure these are set in your .env file."
        )

def create_crew(target_description: str) -> Crew:
    tasks = [
        LeadGenTasks.research_task(target_description),
        LeadGenTasks.analyze_task(),
        LeadGenTasks.document_task()
    ]
    return Crew(
        tasks=tasks,
        verbose=True,
        max_rpm=50,
        process=Process.sequential
    )

def display_lead_metrics(df: pd.DataFrame):
    """Display key metrics and visualizations for the leads data"""
    st.subheader("📊 Lead Analysis Dashboard")
    
    # Key Metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Leads", len(df))
    with col2:
        avg_score = df['Qualification Score'].mean() if 'Qualification Score' in df.columns else 0
        st.metric("Avg Qualification Score", f"{avg_score:.1f}")
    with col3:
        high_priority = len(df[df['Priority'] == 'High']) if 'Priority' in df.columns else 0
        st.metric("High Priority Leads", high_priority)
    with col4:
        platforms = len(df['Platform'].unique()) if 'Platform' in df.columns else 0
        st.metric("Source Platforms", platforms)

    # Create two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Lead Sources Distribution")
        if 'Platform' in df.columns:
            platform_counts = df['Platform'].value_counts()
            fig = px.pie(values=platform_counts.values, 
                        names=platform_counts.index,
                        title="Leads by Platform")
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Qualification Score Distribution")
        if 'Qualification Score' in df.columns:
            fig = px.histogram(df, x='Qualification Score',
                             title="Distribution of Qualification Scores",
                             nbins=10)
            st.plotly_chart(fig, use_container_width=True)

    # Priority Distribution
    if 'Priority' in df.columns:
        st.subheader("Lead Priority Distribution")
        priority_order = ['High', 'Medium', 'Low']
        priority_counts = df['Priority'].value_counts().reindex(priority_order)
        fig = go.Figure(data=[
            go.Bar(x=priority_counts.index, 
                  y=priority_counts.values,
                  marker_color=['#ff0000', '#ffa500', '#00ff00'])
        ])
        fig.update_layout(title="Leads by Priority Level")
        st.plotly_chart(fig, use_container_width=True)

    # Top Leads Table
    if 'Qualification Score' in df.columns:
        st.subheader("🌟 Top Qualified Leads")
        top_leads = df.nlargest(5, 'Qualification Score')[
            ['Username', 'Platform', 'Qualification Score', 'Priority', 'Notes']
        ]
        st.dataframe(top_leads, use_container_width=True)

def display_process_status(phase: str, status: str):
    """Display the current process status"""
    if 'status' not in st.session_state:
        st.session_state.status = {
            "Research": "⏳ Pending",
            "Analysis": "⏳ Pending",
            "Documentation": "⏳ Pending"
        }
    
    st.session_state.status[phase] = status
    
    st.sidebar.subheader("Process Status")
    for phase, state in st.session_state.status.items():
        if "Completed" in state:
            st.sidebar.success(f"{phase}: {state}")
        elif "Processing" in state:
            st.sidebar.info(f"{phase}: {state}")
        elif "Error" in state:
            st.sidebar.error(f"{phase}: {state}")
        else:
            st.sidebar.write(f"{phase}: {state}")

def main():
    st.set_page_config(page_title="AI Lead Generation Agent", layout="wide")
    
    st.title("🎯 AI Lead Generation Agent")
    st.markdown("""
    This AI-powered agent helps you generate and qualify leads by searching across
    multiple platforms including Quora and other relevant sources. Watch the process
    in real-time and explore the results through interactive visualizations.
    """)

    try:
        load_environment()
    except EnvironmentError as e:
        st.error(str(e))
        return

    # Main input
    target_description = st.text_area(
        "Describe what kind of leads you're looking for:",
        placeholder="e.g., Looking for users who need automated video editing software with AI capabilities",
        help="Be specific about the product/service and target audience."
    )

    if st.button("Generate Leads"):
        if not target_description:
            st.error("Please describe your target leads.")
            return

        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize crew
            crew = create_crew(target_description)
            
            # Update status for research phase
            status_text.text("🔍 Phase 1/3: Researching potential leads...")
            display_process_status("Research", "⚡ Processing")
            
            # Execute the crew
            results = crew.kickoff()
            
            # Update final status
            progress_bar.progress(100)
            display_process_status("Research", "✅ Completed")
            display_process_status("Analysis", "✅ Completed")
            display_process_status("Documentation", "✅ Completed")
            status_text.text("✨ Process completed successfully!")
            
            try:
                # Parse results and display
                if isinstance(results, str):
                    results = json.loads(results)
                
                st.success("Lead generation completed successfully!")
                
                # Display file locations
                st.subheader("📁 Generated Files")
                if isinstance(results, dict):
                    if 'csv_file' in results:
                        st.write(f"📊 CSV File: `{results['csv_file']}`")
                    if 'google_sheet_url' in results:
                        st.write(f"📈 Google Sheet: [{results['google_sheet_url']}]({results['google_sheet_url']})")
                    
                    # Load and display data if CSV file exists
                    if 'csv_file' in results and os.path.exists(results['csv_file']):
                        df = pd.read_csv(results['csv_file'])
                        display_lead_metrics(df)
                        
                        # Raw Data Option
                        if st.checkbox("Show Raw Data"):
                            st.subheader("Raw Lead Data")
                            st.dataframe(df)
                else:
                    st.write("Results:", results)
                
            except Exception as e:
                st.error(f"Error processing results: {str(e)}")
                logger.error(f"Error processing results: {str(e)}", exc_info=True)

        except Exception as e:
            status_text.text("❌ Process failed!")
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Process failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()