import sys
import os

# Append the parent directory to sys.path to allow imports from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.state import AgentState
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from ai_service import AIService
from retrieval.statistical_tools import analyze_log_statistics
from retrieval.retriever import get_standard_logs, get_golden_logs

# Define wrappers for the retrieval tools to be used by the agent
@tool
def search_standard_logs(query: str) -> str:
    """Useful for searching the standard, daily operational logs to find errors, warnings, or user actions."""
    return get_standard_logs(query)

@tool
def search_golden_logs(query: str) -> str:
    """Useful for searching the baseline, known-good golden logs. Use this FIRST when asked to compare or find anomalies to understand normal behavior."""
    return get_golden_logs(query)

def investigator_node(state: AgentState) -> dict:
    """
    The Investigator Agent node.
    It uses the baseline profile and tools to investigate the user's query.
    
    Args:
        state (AgentState): The current state of the agent graph.
        
    Returns:
        dict: Updates to the state (investigation_report and messages).
    """
    print("---Executing Investigator Agent Node---")
    
    try:
        # Extract baseline profile and messages from the state
        baseline_profile = state.get("baseline_profile", "No baseline profile available.")
        messages = state.get("messages", [])
        
        # Initialize the AI Service
        ai = AIService()
        llm = ai.get_llm()
        
        # Define the list of tools available to the investigator
        tools = [analyze_log_statistics, search_standard_logs, search_golden_logs]
        
        # Create the dynamic system prompt
        system_prompt = (
            "You are an Investigator Agent for log analysis. "
            "Use your tools to answer the user's query. "
            "Always compare any findings against this Baseline Rulebook:\n"
            f"{baseline_profile}\n"
            "Provide a factual, detailed investigation report."
        )
        
        # Create the ReAct agent executor
        # The 'prompt' argument injects the system prompt.
        agent_executor = create_react_agent(llm, tools, prompt=system_prompt)
        
        # Invoke the agent with the current messages
        result = agent_executor.invoke({"messages": messages})
        
        # Extract the final response (the last message)
        final_message = result["messages"][-1]
        
        # Handle Gemini's list-based content blocks (metadata/signatures)
        if isinstance(final_message.content, list):
            text_blocks = [block.get("text", "") for block in final_message.content if isinstance(block, dict) and block.get("type") == "text"]
            final_response_text = "\n".join(text_blocks)
        else:
            final_response_text = str(final_message.content)
        
        # Return the state update
        return {
            "investigation_report": final_response_text,
            "messages": [final_message]
        }

    except Exception as e:
        # Handle exceptions gracefully
        error_message = f"Error in Investigator Agent: {str(e)}"
        print(error_message)
        return {"investigation_report": error_message}