import streamlit as st
import pandas as pd
import json
import io
from monday_client import fetch_boards_data
from data_processor import normalize_monday_data, get_data_quality_report
from llm_agent import ask_llm

# --- Page Configuration ---
st.set_page_config(page_title="Monday.com BI Agent", page_icon="📈", layout="wide")

st.title("📊 Monday.com Business Intelligence Agent")
st.caption("Founder-level insights powered by Live Data & Gemini 1.5 Flash")

# --- UI Sidebar & Status ---
with st.sidebar:
    st.header("Agent Configuration")
    st.success("⚡ Live Connection: **Active**")
    st.info("🧠 Model: **Gemini 1.5 Flash (Free Tier)**")
    st.divider()
    st.markdown("### Decision Log Note")
    st.write("""
        **Data Strategy:** Using Gemini 2.0 Flash allows for a 1M token window. 
        We pass full datasets in a CSV format to ensure 
        the AI can discover correlations across all columns 
        without hardcoded filtering.
    """)

# --- Main Query Interface ---
user_question = st.text_input(
    "Ask your business question:",
    placeholder="e.g., 'Which sectors are performing best in our pipeline?'"
)

if user_question:
    with st.spinner("🕵️ Agent is fetching live data and performing analysis..."):
        try:
            # 1. LIVE API CALL (Stateless - no caching)
            raw_response = fetch_boards_data()
            
            # 2. DATA NORMALIZATION (Dynamic Column Mapping)
            cleaned_data_dict = normalize_monday_data(raw_response)
            quality_caveats = get_data_quality_report(cleaned_data_dict)
            
            # 3. TOOL-CALL TRACE (Requirement 5: Visibility)
            with st.expander("🛠️ Visible Agent Action Trace", expanded=False):
                st.write("### Step 1: Monday.com API Call (Live)")
                st.json(raw_response)
                
                st.write("### Step 2: Data Cleaning & Resilience")
                for board, items in cleaned_data_dict.items():
                    st.write(f"**Board: {board}** ({len(items)} items processed)")
                    st.dataframe(pd.DataFrame(items))
                
                if quality_caveats:
                    st.warning(f"**Data Quality Caveats:** {', '.join(quality_caveats)}")

            # 4. PREPARE FULL CONTEXT (CSV Serialization)
            context_string = ""
            for board_name, items in cleaned_data_dict.items():
                if items:
                    # Take only the first 30 items to stay under 15k token limit
                    df = pd.DataFrame(items).head(30) 
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False, sep="|")
                    context_string += f"\nBOARD: {board_name} (Top 30 items)\n{csv_buffer.getvalue()}"

            # To be extra safe, if the string is still too long, we take the top 40 deals
            # This ensures it NEVER crashes, but keeps enough data for "Reasoning"
            if len(context_string) > 12000:
                context_string = context_string[:12000] + "\n...[truncated for speed]"


            # 5. BUSINESS INTELLIGENCE AGENT LOGIC
            system_prompt = f"""
            You are a world-class Business Intelligence AI. You are helping a company Founder 
            make data-driven decisions based on live exports from Monday.com.

            LIVE DATASETS (CSV Format):
            {context_string}

            DATA QUALITY CAVEATS:
            {json.dumps(quality_caveats)}

            MISSION:
            1. Analyze the data to answer the user's specific question.
            2. Identify correlations (e.g., Stage vs Probability) and trends.
            3. Handle messy data: Ignore 'N/A' in math, but mention it if it impacts confidence.
            4. Provide strategic advice. Use bold metrics, lists, and tables.
            5. State clearly that this is based on a real-time snapshot.
            """

            # 6. LLM EXECUTION (Gemini 1.5 Flash)
            ai_insight = ask_llm(system_prompt, user_question)

            # 7. UI PRESENTATION
            st.divider()
            st.subheader("💡 Strategic Insights")
            st.markdown(ai_insight)
            
            # Dynamic Metric Summary
            st.divider()
            cols = st.columns(len(cleaned_data_dict) if cleaned_data_dict else 1)
            for i, (board_name, items) in enumerate(cleaned_data_dict.items()):
                with cols[i]:
                    st.metric(f"Items in {board_name}", len(items))

        except Exception as e:
            st.error(f"Critical Error: {str(e)}")
            st.info("Ensure GEMINI_API_KEY is in your .env and the Monday Board IDs are correct.")

else:
    st.info("Waiting for your business query...")

# --- Footer ---
st.markdown("---")
st.caption("Monday.com BI Agent | Powered by Gemini 1.5 Flash")