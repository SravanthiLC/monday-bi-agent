import streamlit as st
import json
import pandas as pd
from monday_client import fetch_boards_data
from data_processor import normalize_monday_data, get_data_quality_report
from llm_agent import ask_llm

# --- Page Config ---
st.set_page_config(page_title="Monday BI Agent", page_icon="📊", layout="wide")

st.title("🚀 Monday.com Business Intelligence Agent")
st.markdown("""
    *Founder-level insights powered by live board data.*
    ---
""")

# --- Sidebar for Status ---
with st.sidebar:
    st.header("System Status")
    st.success("Connected to Monday.com API")
    st.info("Model: Llama-3.3-70b (via Groq)")

# --- Input Section ---
user_question = st.text_input(
    "Ask a business question (e.g., 'What is our total pipeline value for the Energy sector?')",
    placeholder="How's our pipeline looking for the energy sector this quarter?"
)

if user_question:
    with st.spinner("🔄 Fetching live data and analyzing..."):
        try:
            # 1. LIVE API CALL (No Caching)
            raw_data = fetch_boards_data()
            
            # 2. DATA PROCESSING & PRUNING
            # We flatten the messy JSON and identify quality issues
            cleaned_data = normalize_monday_data(raw_data)
            quality_caveats = get_data_quality_report(cleaned_data)
            
            # 3. ACTION TRACE (Problem Statement Requirement)
            with st.expander("🔍 Visible API/Tool-Call Trace"):
                st.write("**Step 1: Monday.com GraphQL Query Executed**")
                st.json(raw_data)
                st.write("**Step 2: Data Normalized & Cleaned**")
                st.write(cleaned_data)
                st.warning(f"**Step 3: Data Quality Caveats Found:** {quality_caveats}")

            # 4. TOKEN MANAGEMENT (The 413 Error Fix)
            # We provide a summary and a limit of 15 items per board to the LLM
            llm_context = {}
            for board_name, items in cleaned_data.items():
                llm_context[board_name] = {
                    "total_count": len(items),
                    "data_sample": items[:15]  # Limit to 15 rows to stay under 12k tokens
                }

            # 5. BUILD FOUNDER-LEVEL PROMPT
            system_prompt = f"""
            You are a high-level Business Intelligence Assistant for a Founder.
            Today's Date: 2026-02-27
            
            GOAL: Provide accurate, concise, and strategic answers based on live data.
            
            LIVE DATA (Samples/Summaries):
            {json.dumps(llm_context, indent=2)}
            
            DATA QUALITY CAVEATS:
            {", ".join(quality_caveats) if quality_caveats else "None detected."}
            
            INSTRUCTIONS:
            - If the user asks for "Pipeline", look at the 'Deals' board.
            - If they ask about "Work" or "Operations", look at 'Work Orders'.
            - If the data is messy or missing (N/A), admit it and explain the impact on your answer.
            - Use bullet points and bold text for key metrics.
            - If a calculation is based on a sample, mention 'based on current board records'.
            """

            # 6. LLM ANALYSIS
            ai_response = ask_llm(system_prompt, user_question)

            # 7. UI PRESENTATION
            st.subheader("💡 Strategic Insight")
            st.markdown(ai_response)
            
            # Additional Polish: Simple Metric View
            if "Deals" in cleaned_data:
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Deals in View", len(cleaned_data["Deals"]))
                with col2:
                    st.metric("Board Status", "Live/Synced")

        except Exception as e:
            st.error(f"Error processing request: {e}")
            st.info("Check your API Keys or Board IDs in the .env file.")

else:
    # Initial State
    st.info("Type a query above to start the live analysis.")
    
    with st.container():
        st.write("### Example Questions you can ask:")
        st.write("- 'Give me a summary of all deals in the Energy sector.'")
        st.write("- 'Compare the number of Work Orders vs. Deals currently active.'")
        st.write("- 'Are there any deals missing critical information like sector or value?'")

# --- Footer ---
st.markdown("---")
st.caption("Monday.com BI Agent Prototype | Tech Stack: Streamlit, Groq (Llama-3), Monday API v2")