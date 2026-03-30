import pytest
import sqlite3
import os
import re
from unittest.mock import patch, MagicMock

from ingestion.teaching_engine import teach_single, parse_and_save_to_sqlite
from retrieval.statistical_tools import analyze_log_statistics
import init_stats_db
from tests.utils.test_logger import logger  # Added our centralized logger

TEST_SQLITE_DB = os.path.join(os.path.dirname(__file__), "temp_stats.db")
DUMMY_LOG_FILE = os.path.join(os.path.dirname(__file__), "dummy_integration.log")

@pytest.fixture(scope="class", autouse=True)
def setup_integration_env():
    """
    SDET Fixture: Creates a self-contained environment for the integration test.
    Generates dummy logs, initializes an isolated SQLite DB, and patches paths.
    """
    logger.info("Initializing isolated SQLite DB for Integration Tests...")
    
    with open(DUMMY_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("2026-01-01 12:00:00 INFO System started\n")
        f.write("2026-01-01 12:05:00 ERROR Connection lost\n")
        f.write("2026-01-01 12:10:00 INFO Reconnected\n")

    if os.path.exists(TEST_SQLITE_DB):
        os.remove(TEST_SQLITE_DB)

    original_join = os.path.join
    
    def smart_path_join(*args):
        if 'logs_stats.db' in args or (len(args) > 0 and args[-1] == 'logs_stats.db'):
            return TEST_SQLITE_DB
        return original_join(*args)

    with patch('init_stats_db.os.path.join', side_effect=smart_path_join):
        init_stats_db.init_stats_db()

    with patch('ingestion.teaching_engine.STATS_DB_PATH', TEST_SQLITE_DB), \
         patch('retrieval.statistical_tools.STATS_DB_PATH', TEST_SQLITE_DB):
        yield

    logger.info("Tearing down Integration Test environment...")
    if os.path.exists(TEST_SQLITE_DB): os.remove(TEST_SQLITE_DB)
    if os.path.exists(DUMMY_LOG_FILE): os.remove(DUMMY_LOG_FILE)


class TestDataIntegration:
    """
    Integration Test Suite: Validates the data flow between the application,
    the SQLite tabular database, and the external data parsing logic.
    """

    def test_tc_int_01_sqlite_parsing_and_insertion(self):
        logger.info("▶️ TC-INT-01: Verifying SQLite parsing and insertion")
        with open(DUMMY_LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        inserted_count = parse_and_save_to_sqlite(lines, DUMMY_LOG_FILE, log_type="app_logs")
        assert inserted_count == 3, f"Expected 3 logs to be parsed, but got {inserted_count}."

        conn = sqlite3.connect(TEST_SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT log_timestamp, log_level, message FROM app_logs")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 3, "Database did not persist the 3 rows."
        assert rows[1][1] == "ERROR", "Log level parsing failed."
        logger.info("✅ TC-INT-01 Passed: SQLite parsing works perfectly.")

    def test_tc_int_02_statistical_tool_execution(self):
        logger.info("▶️ TC-INT-02: Verifying Statistical Tool execution")
        result = analyze_log_statistics.invoke({"log_type": "app_logs"})

        assert "Total Log Entries: 3" in result, "Statistic total count is incorrect."
        assert re.search(r"INFO\s+2", result), "Statistic breakdown for INFO is incorrect."
        assert re.search(r"ERROR\s+1", result), "Statistic breakdown for ERROR is incorrect."
        logger.info("✅ TC-INT-02 Passed: Statistical tool returned correct Pandas output.")

    @patch('ingestion.teaching_engine.Chroma')
    def test_tc_int_03_dual_save_teaching_engine(self, MockChroma):
        logger.info("▶️ TC-INT-03: Verifying Dual-Save Mechanism (VectorDB + SQLite)")
        mock_vectorstore_instance = MagicMock()
        MockChroma.return_value = mock_vectorstore_instance

        result_msg = teach_single(
            file_path=DUMMY_LOG_FILE, start_line=1, end_line=2,
            status="anomaly", explanation="Test anomaly injection",
            save_to_stats=True, log_type="app_logs"
        )

        assert "Success: Knowledge added" in result_msg
        assert mock_vectorstore_instance.add_documents.called, "Vector store insertion failed."
        
        conn = sqlite3.connect(TEST_SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM app_logs")
        total_rows = cursor.fetchone()[0]
        conn.close()

        assert total_rows == 5, "Dual-save did not persist data to SQLite."
        logger.info("✅ TC-INT-03 Passed: Dual-Save works seamlessly.")