import pytest
import os
import time
import sqlite3
from unittest.mock import patch
from langchain_core.messages import HumanMessage

from langgraph.checkpoint.sqlite import SqliteSaver
from agents.supervisor import build_team_graph
import init_stats_db

# Local DB path for the DDT tests
TEST_SQLITE_DB = os.path.join(os.path.dirname(__file__), "ddt_stats.db")

@pytest.fixture(scope="module", autouse=True)
def setup_ddt_database():
    """
    SDET Fixture: Prepares a static, predictable database for the AI 
    to query during the Data-Driven Tests.
    """
    if os.path.exists(TEST_SQLITE_DB):
        os.remove(TEST_SQLITE_DB)

    original_join = os.path.join
    def smart_path_join(*args):
        if 'logs_stats.db' in args or (len(args) > 0 and args[-1] == 'logs_stats.db'):
            return TEST_SQLITE_DB
        return original_join(*args)

    with patch('init_stats_db.os.path.join', side_effect=smart_path_join):
        init_stats_db.init_stats_db()

    # Inject predictable data: 2 ERRORs, 1 INFO
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

    if os.path.exists(TEST_SQLITE_DB):
        os.remove(TEST_SQLITE_DB)


@pytest.fixture(scope="module")
def agent_app():
    """Initializes the AI Graph with an in-memory Checkpointer."""
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    memory = SqliteSaver(conn)
    app = build_team_graph(memory=memory)
    yield app
    conn.close()


def extract_text(content):
    """Safely extracts text from LangChain message content."""
    if isinstance(content, str): return content
    if isinstance(content, list): return " ".join([str(item.get("text", "")) if isinstance(item, dict) else str(item) for item in content])
    return str(content)


@pytest.mark.skipif("GOOGLE_API_KEY" not in os.environ, reason="E2E requires a valid GOOGLE_API_KEY.")
class TestLangGraphDDT:
    """
    Data-Driven Test Suite for the LangGraph AI.
    We pass a list of scenarios to PyTest. PyTest will run this function 
    multiple times automatically, once for each scenario.
    """

    # ------------------ THE TEST DATA (SCENARIOS) ------------------ #
    test_scenarios = [
        (
            "1_Sanity_Check",
            "What are your core capabilities as a DevOps assistant? Answer in one sentence.",
            lambda response: len(response) > 10 and "Error" not in response
        ),
        (
            "2_Data_Extraction_Positive",
            "Check the statistics for 'app_logs'. Exactly how many ERROR logs are recorded?",
            lambda response: "2" in response or "two" in response.lower()
        ),
        (
            "3_Negative_Hallucination_Check",
            "Check the statistics for the table 'flying_pigs_logs'. Tell me what you found.",
            lambda response: "not" in response.lower() or "missing" in response.lower() or "error" in response.lower() or "no such table" in response.lower()
        )
    ]
    # --------------------------------------------------------------- #

    @pytest.mark.parametrize("scenario_name, user_query, validation_logic", test_scenarios)
    def test_ai_intelligence(self, agent_app, scenario_name, user_query, validation_logic):
        """
        Runs the AI agent through the parametrized scenarios.
        """
        print(f"\n[DDT] Running Scenario: {scenario_name}")
        print(f"User Query: {user_query}")

        # Unique thread_id per test so they don't carry over chat history context
        config = {'configurable': {'thread_id': f'ddt_test_{scenario_name}'}}
        initial_state = {"messages": [HumanMessage(content=user_query)]}

        # Invoke AI
        final_state = agent_app.invoke(initial_state, config=config)
        raw_content = final_state["messages"][-1].content
        final_answer = extract_text(raw_content)

        print(f"AI Answer: {final_answer}")

        # Assert based on the dynamic Lambda function defined in the scenarios list
        assert validation_logic(final_answer), f"Validation failed for scenario '{scenario_name}'. AI Answer: {final_answer}"

        # SDET FIX: Anti-Rate-Limit Sleep (Free Tier / Quota Protection)
        print("Sleeping for 5 seconds to respect API quotas before the next question...")
        time.sleep(5)