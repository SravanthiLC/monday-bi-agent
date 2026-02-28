# Monday.com Business Intelligence Agent
A live BI tool designed for company founders to extract strategic insights from Monday.com boards. This agent uses Gemini 2.0 / Gemma 3 to perform cross-board reasoning, identifying trends and correlations between deals and work orders.

## Features
1. Live API Integration: Fetches real-time data from Monday.com with no pre-caching.

2. Token-Optimized Context: Implements a "Pipe-Separated" data compression strategy to fit large boards into free-tier LLM limits.

3. Automated Data Cleaning: Dynamically filters out "N/A" columns and low-signal data to ensure high-quality AI reasoning.

4. Action Traceability: Includes a visible "Agent Trace" in the UI to audit raw API responses and data normalization steps.

5. Zero-Cost Architecture: Built entirely using free-tier tools and APIs.

## Setup Instructions
1. Clone Repository
```bash
git clone git@github.com:SravanthiLC/monday-bi-agent.git
```
2. Install dependencies
```bash
pip install --break-system-packages requirements
```
3. Environment Configuration
Create a .env file in the root directory and add your credentials:
```
MONDAY_API_KEY=
GEMINI_API_KEY=
```
4. Run the Application
```bash
streamlit run app.py
```
## Architectural Decisions
1. Schema-Agnostic Processing: Instead of hardcoding column names, the agent dynamically maps Monday.com column_values to human-readable titles. This allows the AI to "figure out" relationships (e.g., "Does Sector affect Deal Value?") automatically.

2. Resilience Layer: The data_processor.py handles messy data by standardizing null values and stripping high-noise columns (90%+ empty) to stay within the 15k-30k token window of free-tier models.

3. Prompt Engineering: Instructions are passed via a combined system/user prompt to ensure compatibility across different open-source and proprietary models.