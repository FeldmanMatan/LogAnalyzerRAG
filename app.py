import sys
import os
import sqlite3
import warnings

# Suppress specific DeprecationWarning from langgraph
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")

# Setup the path to ensure imports work correctly from the root directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
from retrieval.retriever import get_standard_logs, get_golden_logs
from langchain_core.tools import tool
from retrieval.statistical_tools import analyze_log_statistics
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from ingestion.teaching_engine import teach_single
from agents.batch_analyzer import analyze_log_file_in_batches

@tool
def search_standard_logs(query: str) -> str:
    """Useful for searching the standard, daily operational logs to find errors, warnings, or user actions."""
    return get_standard_logs(query)

@tool
def search_golden_logs(query: str) -> str:
    """Useful for searching the baseline, known-good golden logs. Use this FIRST when asked to compare or find anomalies to understand normal behavior."""
    return get_golden_logs(query)

def extract_clean_text(content):
    """
    Helper function to extract clean text from Gemini's complex response objects.
    Safely handles strings, lists, and nested dictionaries.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text")
    return str(content)

def main():
    # Initialize AIService and get the llm
    ai = AIService()
    llm = ai.get_llm()

    # Create the tools list
    tools = [search_standard_logs, search_golden_logs, analyze_log_statistics]

    # Create SQLite connection
    conn = sqlite3.connect('memory.db', check_same_thread=False)
    # Initialize checkpointer
    memory = SqliteSaver(conn)

    # Create agent
    agent_executor = create_react_agent(llm, tools, checkpointer=memory)

    # Define the config dict
    config = {'configurable': {'thread_id': 'session_1'}}

    print('\n🚀 Welcome to the LogAnalyzer AI. Type "exit" to quit.')

    while True:
        try:
            user_input = input('\n🧑‍💻 You: ')
        except EOFError:
            break

        if user_input.lower() in ['exit', 'quit']:
            break

        if user_input.strip().lower() == 'analyze all':
            file_path = input("📂 Enter log file path to analyze: ").strip()
            chunk_input = input("🔢 Enter chunk size (default 50): ").strip()
            
            # Parse chunk size with default fallback
            try:
                chunk_size = int(chunk_input) if chunk_input else 50
            except ValueError:
                print("Invalid chunk size. Defaulting to 50.")
                chunk_size = 50

            print(f"\n🚀 Starting Batch Analysis on {file_path}...")
            summary = analyze_log_file_in_batches(file_path, chunk_size=chunk_size)
            
            print(f"\n📊 === EXECUTIVE SUMMARY ===\n{summary}\n===========================\n")
            continue

        if user_input.strip().lower() == 'teach':
            try:
                file_path = input("📂 Enter log file path: ")
                start = int(input("🔢 Enter start line: "))
                end = int(input("🔢 Enter end line: "))
                status = input("🏷️ Enter status (golden/anomaly): ")
                explanation = input("🧠 Enter your human explanation: ")

                save_stats_input = input("📊 Save to statistics DB too? (y/n): ")
                save_to_stats = save_stats_input.strip().lower() == 'y'
                log_type = None
                if save_to_stats:
                    log_type = input("📊 Enter log type (e.g., app_logs): ").strip()

                result = teach_single(file_path, start, end, status, explanation, save_to_stats=save_to_stats, log_type=log_type)
                print(f"\n{result}")
            except ValueError:
                print("\nError: Please enter valid numbers for start/end lines.")
            
            continue

        # Check if it's a new conversation by getting the state
        current_state = agent_executor.get_state(config)

        if not current_state.values.get('messages'):
            messages_payload = [("system", "You are a Senior DevOps AI Assistant. You have tools to search standard and golden logs. Always compare them when asked to find anomalies."), ("user", user_input)]
        else:
            messages_payload = [("user", user_input)]

        # Call agent
        response = agent_executor.invoke({"messages": messages_payload}, config=config)

        raw_content = response["messages"][-1].content
        clean_text = extract_clean_text(raw_content)

        print(f'\n🤖 DevOps AI:\n{clean_text}')

if __name__ == "__main__":
    main()