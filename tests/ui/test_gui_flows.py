import pytest
from conftest import wait_for_ui_condition

class TestLogAnalyzerUIFlows:
    """
    High-Impact UI Test Suite for LogAnalyzer GUI.
    Focuses on UI state transitions, component enabling/disabling, and correct backend routing.
    """

    def test_tc01_investigator_chat_flow(self, app):
        """
        TC-01: Verify the Chat interface properly handles inputs, disables controls during
        processing, and renders the AI response.
        """
        # Step 1: Navigate to Chat (Default view, but ensuring explicitly)
        app.show_chat_frame()
        
        # Step 2: Input test query
        test_query = "Analyze the app_logs statistics."
        app.chat_frame.input_entry.insert(0, test_query)
        
        # Step 3: Trigger send message
        app.chat_frame.send_message()
        
        # Step 4: Validate UI state DURING processing (Input disabled, "thinking" text present)
        assert app.chat_frame.input_entry.cget("state") == "disabled", "Input should be disabled during processing."
        chat_text_during = app.chat_frame.chat_history.get("1.0", "end")
        assert "DevOps AI is thinking..." in chat_text_during, "Missing 'thinking' placeholder."
        
        # Step 5: Wait for thread to finish and UI to update
        def is_response_ready():
            text = app.chat_frame.chat_history.get("1.0", "end")
            return "MOCKED_AI_RESPONSE" in text
            
        success = wait_for_ui_condition(app, is_response_ready)
        
        # Step 6: Validate Final UI State
        assert success is True, "Timeout waiting for AI response to render."
        assert app.chat_frame.input_entry.cget("state") == "normal", "Input should be re-enabled."
        assert "DevOps AI is thinking..." not in app.chat_frame.chat_history.get("1.0", "end"), "Placeholder was not removed."

    def test_tc02_batch_analysis_flow(self, app, mocked_backend):
        """
        TC-02: Verify the Batch Analysis UI captures inputs correctly, disables the Run button,
        and displays the executive summary.
        """
        # Step 1: Navigate to Batch Analysis
        app.show_batch_frame()
        
        # Step 2: Inject values (Simulating user input)
        app.batch_frame.file_entry.insert(0, "dummy_large_log.log")
        app.batch_frame.chunk_entry.delete(0, "end")
        app.batch_frame.chunk_entry.insert(0, "100")
        
        # Step 3: Trigger analysis
        app.batch_frame.run_analysis()
        
        # Step 4: Validate UI blocks
        assert app.batch_frame.run_btn.cget("state") == "disabled", "Run button must be disabled during analysis."
        
        # Step 5: Wait for completion
        def is_summary_ready():
            text = app.batch_frame.output_box.get("1.0", "end")
            return "MOCKED_SUMMARY" in text
            
        success = wait_for_ui_condition(app, is_summary_ready)
        
        # Step 6: Assertions
        assert success is True, "Timeout waiting for Batch Analysis summary."
        assert app.batch_frame.run_btn.cget("state") == "normal", "Run button must be re-enabled."
        mocked_backend["batch"].assert_called_once_with("dummy_large_log.log", chunk_size=100)

    def test_tc03_teaching_engine_flow(self, app, mocked_backend):
        """
        TC-03: Verify the Teaching Engine captures complex form data (Dual-Save)
        and calls the backend with the correct types.
        """
        # Step 1: Navigate to Teaching Engine
        app.show_teach_frame()
        
        # Step 2: Fill out the form
        app.teach_frame.file_entry.insert(0, "sample.log")
        app.teach_frame.start_entry.insert(0, "10")
        app.teach_frame.end_entry.insert(0, "20")
        app.teach_frame.status_menu.set("anomaly")
        app.teach_frame.explanation_box.insert("1.0", "Test Explanation")
        
        # Enable Dual-Save
        app.teach_frame.stats_checkbox.select() 
        app.teach_frame.log_type_entry.insert(0, "app_logs")
        
        # Step 3: Submit Knowledge
        app.teach_frame.submit_knowledge()
        
        # Step 4: Wait for success label
        def is_teach_complete():
            return "Success" in app.teach_frame.result_label.cget("text")
            
        success = wait_for_ui_condition(app, is_teach_complete)
        
        # Step 5: Assertions
        assert success is True, "Timeout waiting for Teach completion label."
        assert app.teach_frame.result_label.cget("text_color") == "green", "Success message must be green."
        
        # Verify the backend was called with the exact types and values
        mocked_backend["teach"].assert_called_once_with(
            "sample.log", 
            10, 
            20, 
            "anomaly", 
            "Test Explanation", 
            save_to_stats=True, 
            log_type="app_logs"
        )