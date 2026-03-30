import pytest
import sqlite3
import os
from unittest.mock import patch, MagicMock

# Import the modules we are testing
from ingestion.teaching_engine import teach_single, parse_and_save_to_sqlite
from retrieval.statistical_tools import analyze_log_statistics

# SDET Fix: Define isolated paths locally instead of importing from conftest.py
TEST_SQLITE_DB = os.path.join(os.path.dirname(__file__), "temp_stats.db")
DUMMY_LOG_FILE = os.path.join(os.path.dirname(__file__), "dummy_integration.log")

class TestDataIntegration:
    """
    Integration Test Suite: Validates the data flow between the Python application,
    the SQLite tabular database, and the external data parsing logic.
    """

    def test_tc_int_01_sqlite_parsing_and_insertion(self):
        """
        TC-INT-01: Verify that the Regex parser extracts log data correctly based on
        log_format.json and inserts it into the isolated SQLite database.
        """
        # Step 1: Read the dummy log lines
        with open(DUMMY_LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Step 2: Act - Run the parser explicitly
        inserted_count = parse_and_save_to_sqlite(lines, DUMMY_LOG_FILE, log_type="app_logs")

        # Step 3: Assert Parser Logic
        assert inserted_count == 3, f"Expected 3 logs to be parsed, but got {inserted_count}."

        # Step 4: Assert Database State
        conn = sqlite3.connect(TEST_SQLITE_DB)
        cursor = conn.cursor()
        
        # Verify the table exists and has 3 records
        cursor.execute("SELECT log_timestamp, log_level, message FROM app_logs")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 3, "Database did not persist the 3 rows."
        
        # Verify data integrity (Checking the second log - the ERROR)
        error_row = rows[1]
        assert error_row[0] == "2026-01-01 12:05:00", "Timestamp parsing failed."
        assert error_row[1] == "ERROR", "Log level parsing failed."
        assert error_row[2] == "Connection lost\n", "Message parsing failed."

    def test_tc_int_02_statistical_tool_execution(self):
        """
        TC-INT-02: Verify that the LangGraph tool 'analyze_log_statistics' can correctly
        connect to SQLite, read data, and output accurate Pandas statistics.
        """
        # Act: Execute the tool
        result = analyze_log_statistics.invoke({"log_type": "app_logs"})

        # Assertions
        assert "Total Log Entries: 3" in result, "Statistic total count is incorrect."
        assert "INFO           2" in result, "Statistic breakdown for INFO is incorrect."
        assert "ERROR          1" in result, "Statistic breakdown for ERROR is incorrect."

    @patch('ingestion.teaching_engine.Chroma')
    def test_tc_int_03_dual_save_teaching_engine(self, MockChroma):
        """
        TC-INT-03: Verify the Dual-Save mechanism routes data to both VectorDB and SQLite.
        We mock ChromaDB to avoid API costs during DB tests, but we assert the call 
        was made with the correct Document metadata.
        """
        # Setup Mock Chroma
        mock_vectorstore_instance = MagicMock()
        MockChroma.return_value = mock_vectorstore_instance

        # Act: Trigger a Teach Single command with Dual-Save = True
        result_msg = teach_single(
            file_path=DUMMY_LOG_FILE,
            start_line=1,
            end_line=2,
            status="anomaly",
            explanation="Test anomaly injection",
            save_to_stats=True,
            log_type="app_logs"
        )

        # Assert 1: Successful response
        assert "Success: Knowledge added" in result_msg
        assert "Also added 2 rows" in result_msg

        # Assert 2: ChromaDB Add Documents was called
        assert mock_vectorstore_instance.add_documents.called, "Vector store insertion was not triggered."
        
        # Inspect the Document that was passed to ChromaDB
        added_docs = mock_vectorstore_instance.add_documents.call_args[0][0]
        assert len(added_docs) == 1
        assert added_docs[0].metadata["status"] == "anomaly"
        assert added_docs[0].metadata["human_explanation"] == "Test anomaly injection"
        
        # Assert 3: SQLite received the 2 new rows (Total should now be 5 from previous test)
        conn = sqlite3.connect(TEST_SQLITE_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM app_logs")
        total_rows = cursor.fetchone()[0]
        conn.close()

        assert total_rows == 5, "Dual-save did not persist data to SQLite."