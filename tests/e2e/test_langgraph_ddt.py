import pytest
import os
import time
import sqlite3
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.checkpoint.sqlite import SqliteSaver
from agents.supervisor import build_team_graph
import init_stats_db
from tests.utils.test_logger import logger 

TEST_SQLITE_DB = os.path.join(os.path.dirname(__file__), "ddt_stats.db")

def safe_ai_invoke(agent, initial_state, config):
    """
    SDET Resilience Wrapper: A smart protection mechanism that detects Google Rate Limits,
    pauses execution to allow quota recovery, or aborts the entire run on critical failures.
    """
    try:
        logger.info("Sending prompt to AI model...")
        return agent.invoke(initial_state, config=config)
    
    except Exception as e:
        error_msg = str(e).lower()
        
        # 1. Detect Temporary Rate Limit (HTTP 429)
        if "429" in error_msg or "resource_exhausted" in error_msg or "quota" in error_msg:
            logger.warning("⚠️ Google API Rate Limit Hit (429)! Pausing execution for 120 seconds...")
            time.sleep(120)
            
            try:
                logger.info("🔄 Retrying AI invocation after cooldown...")
                return agent.invoke(initial_state, config=config)
            except Exception as retry_e:
                logger.error("❌ Second attempt failed. Daily Quota likely exhausted.")
                pytest.exit(f"CRITICAL ABORT: API Quota exhausted. Details: {retry_e}")
                
        # 2. Detect Critical Network or Server Errors (HTTP 500/503)
        elif "connection" in error_msg or "503" in error_msg or "timeout" in error_msg:
            logger.error("❌ Critical Network or Server Error detected.")
            pytest.exit(f"CRITICAL ABORT: Network failure. Details: {error_msg}")
            
        # 3. Unhandled bugs
        else:
            logger.error(f"❌ Unhandled AI Exception: {error_msg}")
            raise e

@pytest.fixture(scope="module", autouse=True)
def setup_ddt_database():
    """Prepares a static, predictable database for the Data-Driven Tests."""
    if os.path.exists(TEST_SQLITE_DB): os.remove(TEST_SQLITE_DB)

    original_join = os.path.join
    def smart_path_join(*args):
        if 'logs_stats.db' in args or (len(args) > 0 and args[-1] == 'logs_stats.db'): return TEST_SQLITE_DB
        return original_join(*args)

    with patch('init_stats_db.os.path.join', side_effect=smart_path_join):
        init_stats_db.init_stats_db()

    conn = sqlite3.connect(TEST_SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO app_logs (source_file, log_timestamp, log_level, message)
        VALUES ('test1.log', '2026-01-01 10:00', 'ERROR', 'Timeout'),
               ('test1.log', '2026-01-01 10:05', 'ERROR', 'Crash'),
               ('test2.log', '2026-01-01 10:10', 'INFO', 'Started')
    """)
    conn.commit()
    conn.close()

    with patch('ingestion.teaching_engine.STATS_DB_PATH', TEST_SQLITE_DB), \
         patch('retrieval.statistical_tools.STATS_DB_PATH', TEST_SQLITE_DB):
        yield

    if os.path.exists(TEST_SQLITE_DB): os.remove(TEST_SQLITE_DB)


@pytest.fixture(scope="module")
def agent_app():
    """Initializes the AI Graph with an in-memory Checkpointer."""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    memory = SqliteSaver(conn)
    app = build_team_graph(memory=memory)
    yield app
    conn.close()

def extract_text(content):
    """Safely extracts plain text from LangChain message content."""
    if isinstance(content, str): return content
    if isinstance(content, list): return " ".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content])
    return str(content)

@pytest.mark.skipif("GOOGLE_API_KEY" not in os.environ, reason="E2E requires a valid GOOGLE_API_KEY.")
class TestLangGraphDDT:
    
    # Define Data-Driven Test Scenarios (Name, Prompt, Validation Lambda)
    test_scenarios = [
        (
            "1_Sanity_Check",
            "What are your core capabilities as a DevOps assistant? Answer in one sentence.",
            lambda response: len(response) > 10 and "error" not in response.lower()
        ),
        (
            "2_Data_Extraction",
            "Check the statistics for 'app_logs'. Exactly how many ERROR logs are recorded?",
            lambda response: "2" in response or "two" in response.lower()
        ),
        (
            "3_Negative_Hallucination",
            "Check the statistics for the table 'flying_pigs'. Tell me what you found.",
            lambda response: "not" in response.lower() or "missing" in response.lower() or "error" in response.lower() or "no such table" in response.lower()
        )
    ]

    @pytest.mark.parametrize("scenario_name, user_query, validation_logic", test_scenarios)
    def test_ai_intelligence(self, agent_app, scenario_name, user_query, validation_logic):
        logger.info(f"▶️ Starting Scenario: {scenario_name}")
        logger.debug(f"User Query: {user_query}")
        
        # Unique thread_id prevents conversational memory bleed between tests
        config = {'configurable': {'thread_id': f'ddt_test_{scenario_name}'}}
        initial_state = {"messages": [HumanMessage(content=user_query)]}

        # Invoke AI using the Resilience Wrapper
        final_state = safe_ai_invoke(agent_app, initial_state, config)
        
        last_message = final_state["messages"][-1]
        assert isinstance(last_message, AIMessage), "Expected AIMessage from LangGraph."
        
        final_answer = extract_text(last_message.content)
        logger.debug(f"AI Answer: {final_answer}")

        assert validation_logic(final_answer), f"Validation failed for '{scenario_name}'"
        logger.info(f"✅ Scenario {scenario_name} Passed successfully.")

        # Respect API quotas between successful calls
        logger.info("Sleeping for 10 seconds to respect base API quotas...")
        time.sleep(10)