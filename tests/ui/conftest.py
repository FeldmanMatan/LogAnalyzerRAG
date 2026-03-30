import pytest
import time
import threading
from unittest.mock import MagicMock, patch

# Import the UI application
from gui_app import LogAnalyzerUI

@pytest.fixture(autouse=True)
def force_sync_threads(monkeypatch):
    """
    SDET Trick: Forces all background threads to run synchronously in the main thread.
    This bypasses the Tkinter 'RuntimeError: main thread is not in main loop' 
    and makes UI testing 100% deterministic and fast.
    """
    def sync_start(self):
        # Instead of spawning a background thread, execute the target function directly
        self.run()
        
    # Overwrite threading.Thread.start globally for all tests in this session
    monkeypatch.setattr(threading.Thread, 'start', sync_start)

@pytest.fixture(scope="class")
def mocked_backend():
    """
    Class-scoped mock: Maintains the mocks across the entire test suite class.
    Isolates the UI from actual API calls to LLMs or Vector Databases.
    """
    with patch('gui_app.analyze_log_file_in_batches') as mock_batch, \
         patch('gui_app.teach_single') as mock_teach:
        
        # Configure deterministic returns for our automated tests
        mock_batch.return_value = "MOCKED_SUMMARY: Batch analysis completed successfully."
        mock_teach.return_value = "Success: Knowledge added to vector store (MOCKED)."
        
        yield {"batch": mock_batch, "teach": mock_teach}

@pytest.fixture(scope="class")
def app(mocked_backend):
    """
    Class-scoped app: Opens the CustomTkinter UI ONCE for all tests in the class. 
    Prevents the dreaded Tkinter 'tcl_findLibrary' memory corruption error caused 
    by rapid destroy/init cycles.
    """
    # Initialize the main UI application
    ui_app = LogAnalyzerUI()
    
    # Mock the internal LangGraph agent_app inside the UI
    ui_app.agent_app = MagicMock()
    mock_response = {
        "messages": [MagicMock(content="MOCKED_AI_RESPONSE: Baseline analysis is normal.")]
    }
    ui_app.agent_app.invoke.return_value = mock_response
    
    # Render UI components initially before yielding to tests
    ui_app.update() 
    yield ui_app
    
    # Teardown: Destroy the UI only after ALL tests in the class have finished
    ui_app.destroy()

def wait_for_ui_condition(app, condition_func, timeout=5.0):
    """
    Helper function to wait for a UI state change by polling Tkinter's event loop.
    Crucial for testing asynchronous UI updates without hard sleep() statements.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        app.update() # Process pending background UI events
        if condition_func():
            return True
        time.sleep(0.1)
    return False