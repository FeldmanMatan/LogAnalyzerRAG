import sys
import os

# Append the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_service import AIService
from retrieval.retriever import get_standard_logs, get_golden_logs
from langchain_core.tools import tool

# The CORRECT and MODERN import for LangChain V1.0+ (No warnings!)
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

def run_agent():
    # Instantiate AIService and get the llm model
    ai = AIService()
    llm = ai.get_llm()

    # Create a list of tools
    tools = [search_standard_logs, search_golden_logs]

    # Create the modern agent using the official V1.0 method
    agent_executor = create_agent(llm, tools)

    print("🚀 Starting the Agentic RAG Analysis...\n")
    
    # Version-Proof execution: Pass the system prompt as the first message
    response = agent_executor.invoke({
        "messages": [
            ("system", "You are a Senior DevOps AI Assistant. You have tools to search both standard logs and golden baseline logs. Always use the tools to find information before answering. If asked to find anomalies, compare the standard logs against the golden logs."),
            ("user", "Compare the memory usage in the standard logs versus the golden baseline logs. What is the difference?")
        ]
    })

    # Beautifully print the agent's thought process
    for msg in response["messages"]:
        msg_type = msg.__class__.__name__
        
        if msg_type == "AIMessage" and msg.tool_calls:
            print(f"🤖 Agent Thought: I need to use a tool -> [{msg.tool_calls[0]['name']}]")
        elif msg_type == "ToolMessage":
            print(f"🛠️ Tool Result: Retrieved data from logs.")
        elif msg_type == "AIMessage" and not msg.tool_calls:
            clean_text = extract_clean_text(msg.content)
            print(f"\n✅ Final Answer:\n{clean_text}\n")

if __name__ == "__main__":
    run_agent()