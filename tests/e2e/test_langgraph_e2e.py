import pytest
import os
import sqlite3
from langchain_core.messages import HumanMessage, AIMessage

# Import the graph builder
from langgraph.checkpoint.sqlite import SqliteSaver
from agents.supervisor import build_team_graph

def extract_test_text(content):
    """
    Helper to extract plain text from LangChain message content,
    which can be either a string or a list of blocks when tools are used.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content])
    return str(content)

@pytest.fixture(scope="class")
def agent_app():
    """
    SDET Fixture: Initializes the LangGraph multi-agent system with an 
    isolated in-memory SQLite database just for E2E testing.
    """
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    memory = SqliteSaver(conn)
    app = build_team_graph(memory=memory)
    yield app
    conn.close()

TEST_CONFIG = {'configurable': {'thread_id': 'e2e_test_session'}}

@pytest.mark.skipif("GOOGLE_API_KEY" not in os.environ, reason="E2E tests require a valid GOOGLE_API_KEY.")
class TestLangGraphAgenticWorkflow:

    def test_tc_e2e_01_supervisor_routing_and_response_structure(self, agent_app):
        """
        TC-E2E-01: Verify that the multi-agent system processes a general query,
        does not crash, and returns a substantial string (Markdown expected).
        """
        print("\n[E2E Test] Invoking LangGraph AI Agents... (This may take 10-20 seconds)")
        
        user_input = "You are a DevOps assistant. Give me a 1 sentence summary of your capabilities."
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        
        final_state = agent_app.invoke(initial_state, config=TEST_CONFIG)
        
        assert "messages" in final_state, "The graph state must contain a 'messages' key."
        assert len(final_state["messages"]) >= 2, "Expected at least User prompt and AI response."
        
        final_message = final_state["messages"][-1]
        assert isinstance(final_message, AIMessage), "The final message must be an AIMessage object."
        
        # Use our safe text extractor
        content = extract_test_text(final_message.content)
        print(f"\n[AI Response Output]:\n{content}\n")
        
        assert len(content) > 20, "The AI returned an abnormally short or empty response."
        assert "Error" not in content, "The AI returned an error string instead of a valid response."

    def test_tc_e2e_02_statistical_tool_triggering(self, agent_app):
        """
        TC-E2E-02: Force the AI to use a specific Tool (Statistical Analysis).
        """
        print("\n[E2E Test] Forcing AI to use the SQLite Statistical Tool...")
        
        user_input = "Please check the statistics for 'app_logs'. If the table doesn't exist, just tell me it is missing."
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        
        final_state = agent_app.invoke(initial_state, config=TEST_CONFIG)
        
        # Safely extract text whether it's a string or a list of tool-call dicts
        raw_content = final_state["messages"][-1].content
        final_message_content = extract_test_text(raw_content)
        
        is_data_returned = "Total Log Entries" in final_message_content
        is_missing_handled = "not exist" in final_message_content.lower() or "not found" in final_message_content.lower() or "missing" in final_message_content.lower()
        
        assert is_data_returned or is_missing_handled, \
            f"The AI failed to use the tool correctly or hallucinated. Output was: {final_message_content}"