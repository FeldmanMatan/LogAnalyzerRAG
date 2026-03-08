import sys
import os

# Setup the path to ensure imports work correctly from the root directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService
from retrieval.retriever import get_standard_logs, get_golden_logs
from langchain_core.tools import tool
from langchain.agents import create_agent

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
    tools = [search_standard_logs, search_golden_logs]

    # Create the agent executor
    agent_executor = create_agent(llm, tools)

    # Initialize chat history with system prompt
    chat_history = [("system", "You are a Senior DevOps AI Assistant. You have tools to search standard and golden logs. Always compare them when asked to find anomalies.")]

    print('\n🚀 Welcome to the LogAnalyzer AI. Type "exit" to quit.')

    while True:
        try:
            user_input = input('\n🧑‍💻 You: ')
        except EOFError:
            break

        if user_input.lower() in ['exit', 'quit']:
            break

        chat_history.append(("user", user_input))

        # Call agent
        response = agent_executor.invoke({"messages": chat_history})

        raw_content = response["messages"][-1].content
        clean_text = extract_clean_text(raw_content)

        print(f'\n🤖 DevOps AI:\n{clean_text}')

        chat_history.append(("assistant", clean_text))

if __name__ == "__main__":
    main()