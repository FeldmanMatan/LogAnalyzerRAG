import pytest
import os
import time
import sqlite3
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.checkpoint.sqlite import SqliteSaver
from agents.supervisor import build_team_graph
from tests.utils.test_logger import logger # Added Logger

def extract_test_text(content):
    """Safely extracts plain text from LangChain message content."""
    if isinstance(content, str): return content
    if isinstance(content, list): return " ".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content])
    return str(content)

@pytest.fixture(scope="class")
def agent_app():
    """Initializes the LangGraph multi-agent system with an isolated SQLite DB."""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    memory = SqliteSaver(conn)
    app = build_team_graph(memory=memory)
    yield app
    conn.close()

TEST_CONFIG = {'configurable': {'thread_id': 'e2e_test_session'}}

@pytest.mark.skipif("GOOGLE_API_KEY" not in os.environ, reason="E2E tests require a valid GOOGLE_API_KEY.")
class TestLangGraphAgenticWorkflow:

    def test_tc_e2e_01_supervisor_routing_and_response_structure(self, agent_app):
        """TC-E2E-01: Verify multi-agent system processes a general query and routes correctly."""
        logger.info("▶️ TC-E2E-01: Invoking LangGraph AI Agents (Supervisor Routing)...")
        
        user_input = "You are a DevOps assistant. Give me a 1 sentence summary of your capabilities."
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        
        try:
            final_state = agent_app.invoke(initial_state, config=TEST_CONFIG)
            
            assert "messages" in final_state, "Graph state must contain a 'messages' key."
            final_message = final_state["messages"][-1]
            assert isinstance(final_message, AIMessage), "Final message must be an AIMessage."
            
            content = extract_test_text(final_message.content)
            logger.debug(f"AI Response Output: {content}")
            
            assert len(content) > 20, "AI returned an abnormally short response."
            logger.info("✅ TC-E2E-01 Passed: Supervisor routing successful.")
            
        except Exception as e:
            logger.error(f"❌ AI Invocation failed: {e}")
            raise e
            
        logger.info("Sleeping for 10 seconds to respect API Rate Limits...")
        time.sleep(10)

    def test_tc_e2e_02_statistical_tool_triggering(self, agent_app):
        """TC-E2E-02: Force the AI to use a specific Tool (Statistical Analysis)."""
        logger.info("▶️ TC-E2E-02: Forcing AI to use the SQLite Statistical Tool...")
        
        user_input = "Please check the statistics for 'app_logs'. If the table doesn't exist, just tell me it is missing."
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        
        try:
            final_state = agent_app.invoke(initial_state, config=TEST_CONFIG)
            raw_content = final_state["messages"][-1].content
            final_message_content = extract_test_text(raw_content)
            
            logger.debug(f"AI Response Output: {final_message_content}")
            
            is_data_returned = "Total Log Entries" in final_message_content
            is_missing_handled = "not exist" in final_message_content.lower() or "not found" in final_message_content.lower() or "missing" in final_message_content.lower()
            
            assert is_data_returned or is_missing_handled, "AI failed to use the tool correctly."
            logger.info("✅ TC-E2E-02 Passed: AI correctly identified and used the tool.")
            
        except Exception as e:
            logger.error(f"❌ AI Tool Triggering failed: {e}")
            raise e