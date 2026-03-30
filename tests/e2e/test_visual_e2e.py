import pytest
import time
import os
import sqlite3
import threading
import tkinter
from unittest.mock import patch

from gui_app import LogAnalyzerUI
import init_stats_db
from tests.utils.test_logger import logger  # Added our centralized logger

# Real test paths for the Visual E2E
TEST_SQLITE_DB = os.path.join(os.path.dirname(__file__), "e2e_stats.db")
TEST_DUMMY_LOG = os.path.join(os.path.dirname(__file__), "visual_dummy.log")

class SafeUIQueue:
    """
    SDET Design Pattern: A Context Manager that safely intercepts Tkinter background
    updates from LangGraph threads and queues them for the main UI loop.
    This keeps tests clean and prevents 'main thread is not in main loop' crashes.
    """
    def __init__(self):
        self.task_queue = []
        self.main_thread_id = threading.get_ident()
        self.original_after = tkinter.Misc.after
        self.original_winfo = tkinter.Misc.winfo_toplevel

    def __enter__(self):
        queue_ref = self.task_queue
        main_id = self.main_thread_id
        orig_after = self.original_after
        orig_winfo = self.original_winfo

        def safe_after(self_obj, ms, func=None, *args):
            if threading.get_ident() != main_id:
                if func: queue_ref.append((func, args))
            else:
                return orig_after(self_obj, ms, func, *args)

        def safe_winfo(self_obj):
            if threading.get_ident() != main_id:
                class DummyToplevel:
                    def after(self, ms, func, *args):
                        queue_ref.append((func, args))
                return DummyToplevel()
            return orig_winfo(self_obj)

        tkinter.Misc.after = safe_after
        tkinter.Misc.winfo_toplevel = safe_winfo
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        tkinter.Misc.after = self.original_after
        tkinter.Misc.winfo_toplevel = self.original_winfo

    def process(self):
        """Executes the queued background tasks on the main UI thread."""
        while self.task_queue:
            func, args = self.task_queue.pop(0)
            func(*args)


@pytest.fixture(scope="module", autouse=True)
def setup_real_data_for_visual_test():
    """
    SDET Fixture: Prepares REAL data and a dummy log file for the Visual UI Robot.
    """
    logger.info("Setting up real data and environment for Visual E2E Tests...")
    
    # Create Dummy Log File for Batch/Teach tests
    with open(TEST_DUMMY_LOG, 'w', encoding='utf-8') as f:
        f.write("2026-01-01 10:00 ERROR Network timeout\n" * 20)
        
    if os.path.exists(TEST_SQLITE_DB):
        os.remove(TEST_SQLITE_DB)
        
    original_join = os.path.join
    def smart_path_join(*args):
        if 'logs_stats.db' in args or (len(args) > 0 and args[-1] == 'logs_stats.db'):
            return TEST_SQLITE_DB
        return original_join(*args)

    with patch('init_stats_db.os.path.join', side_effect=smart_path_join):
        init_stats_db.init_stats_db()
        
    conn = sqlite3.connect(TEST_SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO app_logs (source_file, log_timestamp, log_level, message) 
        VALUES ('demo.log', '2026-01-01 10:00', 'ERROR', 'Database timeout'),
               ('demo.log', '2026-01-01 10:05', 'ERROR', 'Connection refused')
    """)
    conn.commit()
    conn.close()
    
    with patch('ingestion.teaching_engine.STATS_DB_PATH', TEST_SQLITE_DB), \
         patch('retrieval.statistical_tools.STATS_DB_PATH', TEST_SQLITE_DB):
        yield
        
    logger.info("Tearing down Visual E2E environment...")
    if os.path.exists(TEST_SQLITE_DB): os.remove(TEST_SQLITE_DB)
    if os.path.exists(TEST_DUMMY_LOG): os.remove(TEST_DUMMY_LOG)


@pytest.mark.skipif("GOOGLE_API_KEY" not in os.environ, reason="Visual E2E requires a valid GOOGLE_API_KEY.")
class TestVisualE2E:
    """
    Visual End-to-End Test Suite. 
    Simulates human interactions with the Tkinter GUI.
    """

    def type_like_human(self, app, widget, text, speed_ms=0.03):
        """Helper function to simulate human typing for realism."""
        if hasattr(widget, "insert") and "Text" in str(type(widget)):
            widget.delete("1.0", "end")
            widget.insert("1.0", text)
            app.update()
            time.sleep(speed_ms * len(text))
        else:
            widget.delete(0, "end")
            for char in text:
                widget.insert("end", char)
                app.update() 
                time.sleep(speed_ms)

    def test_tc_vis_01_chat_flow(self):
        """TC-VIS-01: Visual check of the Investigator Chat."""
        logger.info("▶️ TC-VIS-01: Running Visual Chat Flow...")
        with SafeUIQueue() as ui_queue:
            app = LogAnalyzerUI()
            app.update()
            time.sleep(1)

            app.show_chat_frame()
            app.update()
            
            test_query = "Check the statistics for 'app_logs'. How many ERROR logs?"
            logger.debug(f"Simulating human typing: {test_query}")
            self.type_like_human(app, app.chat_frame.input_entry, test_query)
            app.chat_frame.send_message()
            
            start_time = time.time()
            success = False
            while time.time() - start_time < 30:
                app.update() 
                ui_queue.process() 
                
                current_text = app.chat_frame.chat_history.get("1.0", "end")
                if "DevOps AI is thinking..." not in current_text and len(current_text.strip()) > len(test_query) + 10:
                    success = True
                    break
                time.sleep(0.1) 
                
            if success:
                time.sleep(2) 
            
            final_text = app.chat_frame.chat_history.get("1.0", "end")
            app.destroy() 
            
            assert success is True, "AI Chat timed out (Likely API Rate Limit)."
            assert "2" in final_text or "two" in final_text.lower(), "AI failed to find the 2 errors."
            logger.info("✅ TC-VIS-01 Passed: Visual Chat Flow successful.")
            
        logger.info("Sleeping to cool down API quota...")
        time.sleep(10)

    def test_tc_vis_02_batch_analysis_flow(self):
        """TC-VIS-02: Visual check of the Map-Reduce Batch Analysis."""
        logger.info("▶️ TC-VIS-02: Running Visual Batch Analysis Flow...")
        with SafeUIQueue() as ui_queue:
            app = LogAnalyzerUI()
            app.update()
            time.sleep(1)

            app.show_batch_frame()
            app.update()
            time.sleep(0.5)

            logger.debug("Filling Batch Analysis form...")
            self.type_like_human(app, app.batch_frame.file_entry, TEST_DUMMY_LOG)
            app.batch_frame.chunk_entry.delete(0, "end")
            self.type_like_human(app, app.batch_frame.chunk_entry, "10")
            
            app.batch_frame.run_analysis()
            
            start_time = time.time()
            success = False
            while time.time() - start_time < 45: 
                app.update()
                ui_queue.process()
                
                output = app.batch_frame.output_box.get("1.0", "end")
                if "EXECUTIVE SUMMARY" in output or "completed" in output.lower():
                    success = True
                    break
                time.sleep(0.1)

            if success:
                time.sleep(3) 
                
            app.destroy()
            assert success is True, "Batch Analysis timed out."
            logger.info("✅ TC-VIS-02 Passed: Visual Batch Analysis successful.")
            
        logger.info("Sleeping to cool down API quota...")
        time.sleep(10)

    def test_tc_vis_03_teaching_engine_flow(self):
        """TC-VIS-03: Visual check of the Teaching Engine and Dual-Save."""
        logger.info("▶️ TC-VIS-03: Running Visual Teaching Engine Flow...")
        with SafeUIQueue() as ui_queue:
            app = LogAnalyzerUI()
            app.update()
            time.sleep(1)

            app.show_teach_frame()
            app.update()
            time.sleep(0.5)

            logger.debug("Filling Teaching Engine form...")
            self.type_like_human(app, app.teach_frame.file_entry, TEST_DUMMY_LOG)
            self.type_like_human(app, app.teach_frame.start_entry, "1")
            self.type_like_human(app, app.teach_frame.end_entry, "5")
            
            app.teach_frame.status_menu.set("anomaly")
            app.update()
            
            self.type_like_human(app, app.teach_frame.explanation_box, "Critical Visual Test Anomaly")
            
            app.teach_frame.stats_checkbox.select()
            self.type_like_human(app, app.teach_frame.log_type_entry, "app_logs")
            
            app.teach_frame.submit_knowledge()
            
            start_time = time.time()
            success = False
            while time.time() - start_time < 20:
                app.update()
                ui_queue.process()
                
                result_text = app.teach_frame.result_label.cget("text")
                if "Success" in result_text or "Error" in result_text:
                    success = True
                    break
                time.sleep(0.1)

            if success:
                time.sleep(2)
                
            final_status = app.teach_frame.result_label.cget("text")
            app.destroy()
            
            assert success is True, "Teaching Engine timed out."
            assert "Success" in final_status, f"Teaching Engine failed with error: {final_status}"
            logger.info("✅ TC-VIS-03 Passed: Visual Teaching Engine flow successful.")