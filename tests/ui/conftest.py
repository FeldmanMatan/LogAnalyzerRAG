import pytest
import time
import threading
from unittest.mock import MagicMock, patch

from gui_app import LogAnalyzerUI
from tests.utils.test_logger import logger # Added Logger

@pytest.fixture(autouse=True)
def force_sync_threads(monkeypatch):
    """SDET Trick: Forces background threads to run synchronously to prevent Tkinter crashes."""
    def sync_start(self):
        self.run()
    monkeypatch.setattr(threading.Thread, 'start', sync_start)

@pytest.fixture(scope="class")
def mocked_backend():
    """Class-scoped mock: Isolates the UI from actual API calls to LLMs."""
    logger.info("Initializing Mocked Backend for UI Tests...")
    with patch('gui_app.analyze_log_file_in_batches') as mock_batch, \
         patch('gui_app.teach_single') as mock_teach:
        
        mock_batch.return_value = "MOCKED_SUMMARY: Batch analysis completed successfully."
        mock_teach.return_value = "Success: Knowledge added to vector store (MOCKED)."
        
        yield {"batch": mock_batch, "teach": mock_teach}

@pytest.fixture(scope="class")
def app(mocked_backend):
    """Opens the CustomTkinter UI ONCE for all tests in the class."""
    logger.info("Booting up CustomTkinter UI App for testing...")
    ui_app = LogAnalyzerUI()
    
    ui_app.agent_app = MagicMock()
    mock_response = {"messages": [MagicMock(content="MOCKED_AI_RESPONSE: Baseline analysis is normal.")]}
    ui_app.agent_app.invoke.return_value = mock_response
    
    ui_app.update() 
    yield ui_app
    
    logger.info("Destroying UI App after tests completion.")
    ui_app.destroy()

def wait_for_ui_condition(app, condition_func, timeout=5.0):
    """Helper function to wait for a UI state change by polling Tkinter's event loop."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        app.update() 
        if condition_func(): return True
        time.sleep(0.1)
    return False