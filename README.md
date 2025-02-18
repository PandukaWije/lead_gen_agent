# AI Lead Generation Agent 🎯

A powerful AI-powered lead generation system that helps you find, analyze, and qualify potential leads across multiple platforms including Quora and other relevant sources.

## 🌟 Features

- Multi-platform lead research using Exa and Quora
- Automated lead qualification and scoring
- Real-time process tracking and visualization
- Export capabilities to both CSV and Google Sheets
- Interactive dashboard with lead metrics and analytics
- Streamlit-based user interface

## 🏗️ Project Structure

```
.
├── agents/
│   ├── analyzer_agent.py    # Lead qualification agent
│   ├── researcher_agent.py  # Lead research agent
│   └── writer_agent.py      # Data management agent
├── tasks/
│   └── tasks.py            # Task definitions for agents
├── tools/
│   ├── csv_tools.py        # CSV export functionality
│   ├── exa_tools.py        # Exa search integration
│   ├── quora_tools.py      # Quora search integration
│   └── sheets_tools.py     # Google Sheets integration
├── app.py                  # Main Streamlit application
└── ai_lead_generation_agent.py  # Core lead generation logic
```

## 🚀 Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-lead-generation-agent.git
cd ai-lead-generation-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following API keys:
```
OPENAI_API_KEY=your_openai_api_key
EXA_API_KEY=your_exa_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
COMPOSIO_API_KEY=your_composio_api_key
```

## 🔧 Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Enter your target lead description in the text area.

3. Click "Generate Leads" to start the process.

4. Monitor the progress in real-time through the status indicators.

5. View results in the interactive dashboard and download the generated files.

## 📊 Output Formats

The system generates leads in two formats:

1. CSV File (Required)
   - Automatically generated with timestamp
   - Contains all lead data and qualification metrics
   - Stored in `lead_generation_output/` directory

2. Google Sheet (Optional)
   - Created if Google Sheets integration is successful
   - Provides collaborative access to lead data
   - Includes all fields from the CSV

## 🤖 Agent System

The system uses three specialized AI agents:

1. **Research Agent**
   - Searches across platforms for potential leads
   - Uses Exa and Quora integration
   - Identifies active discussions and interested users

2. **Analyzer Agent**
   - Qualifies and scores leads
   - Evaluates conversion likelihood
   - Assigns priority levels

3. **Writer Agent**
   - Manages data organization
   - Handles export to CSV and Google Sheets
   - Ensures data consistency

## 📈 Dashboard Features

- Total lead count and average qualification scores
- Lead source distribution visualization
- Qualification score distribution
- Priority level breakdown
- Top qualified leads table
- Raw data access

## ⚠️ Requirements

- Python 3.8+
- Access to required API services (OpenAI, Exa, Firecrawl, Composio)
- Sufficient API credits for lead generation
- Internet connection for platform searches

## 🔒 Security Note

This application requires API keys for various services. Always keep your `.env` file secure and never commit it to version control.

## 📝 License

MIT License - feel free to use and modify as needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
