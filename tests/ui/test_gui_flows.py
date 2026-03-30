import pytest
from conftest import wait_for_ui_condition
from tests.utils.test_logger import logger # Added Logger

class TestLogAnalyzerUIFlows:
    """High-Impact UI Test Suite for LogAnalyzer GUI."""

    def test_tc01_investigator_chat_flow(self, app):
        logger.info("▶️ TC-UI-01: Verifying Investigator Chat Flow")
        app.show_chat_frame()
        
        test_query = "Analyze the app_logs statistics."
        app.chat_frame.input_entry.insert(0, test_query)
        logger.debug(f"Inputted query: {test_query}")
        
        app.chat_frame.send_message()
        
        assert app.chat_frame.input_entry.cget("state") == "disabled", "Input should be disabled."
        
        def is_response_ready():
            return "MOCKED_AI_RESPONSE" in app.chat_frame.chat_history.get("1.0", "end")
            
        success = wait_for_ui_condition(app, is_response_ready)
        
        assert success is True, "Timeout waiting for AI response to render."
        assert app.chat_frame.input_entry.cget("state") == "normal", "Input should be re-enabled."
        logger.info("✅ TC-UI-01 Passed: Chat flow renders correctly.")

    def test_tc02_batch_analysis_flow(self, app, mocked_backend):
        logger.info("▶️ TC-UI-02: Verifying Batch Analysis UI Flow")
        app.show_batch_frame()
        
        app.batch_frame.file_entry.insert(0, "dummy_large_log.log")
        app.batch_frame.chunk_entry.delete(0, "end")
        app.batch_frame.chunk_entry.insert(0, "100")
        
        app.batch_frame.run_analysis()
        assert app.batch_frame.run_btn.cget("state") == "disabled", "Run button must be disabled."
        
        def is_summary_ready():
            return "MOCKED_SUMMARY" in app.batch_frame.output_box.get("1.0", "end")
            
        success = wait_for_ui_condition(app, is_summary_ready)
        
        assert success is True, "Timeout waiting for Batch Analysis summary."
        assert app.batch_frame.run_btn.cget("state") == "normal", "Run button must be re-enabled."
        logger.info("✅ TC-UI-02 Passed: Batch analysis UI responds correctly.")

    def test_tc03_teaching_engine_flow(self, app, mocked_backend):
        logger.info("▶️ TC-UI-03: Verifying Teaching Engine (Dual-Save) UI Flow")
        app.show_teach_frame()
        
        app.teach_frame.file_entry.insert(0, "sample.log")
        app.teach_frame.start_entry.insert(0, "10")
        app.teach_frame.end_entry.insert(0, "20")
        app.teach_frame.status_menu.set("anomaly")
        app.teach_frame.explanation_box.insert("1.0", "Test Explanation")
        
        app.teach_frame.stats_checkbox.select() 
        app.teach_frame.log_type_entry.insert(0, "app_logs")
        
        app.teach_frame.submit_knowledge()
        
        def is_teach_complete():
            return "Success" in app.teach_frame.result_label.cget("text")
            
        success = wait_for_ui_condition(app, is_teach_complete)
        
        assert success is True, "Timeout waiting for Teach completion label."
        logger.info("✅ TC-UI-03 Passed: Teaching Engine form captured and submitted data.")