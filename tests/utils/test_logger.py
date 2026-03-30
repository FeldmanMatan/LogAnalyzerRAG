import logging
import os
from datetime import datetime

# --- Custom SDET Logger Class ---
class AutomationLogger(logging.Logger):
    """
    Custom Logger designed specifically for Test Automation.
    Adds specialized methods for logging test steps and statuses.
    """
    def step(self, step_number: int, message: str):
        """Logs a formatted test step."""
        self.info(f"  ▶ STEP {step_number}: {message}")
        
    def validation(self, message: str):
        """Logs a validation/assertion checkpoint."""
        self.info(f"  🔍 VALIDATION: {message}")

def setup_logger():
    # Register the custom logger class
    logging.setLoggerClass(AutomationLogger)
    
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M")
    log_file = os.path.join(log_dir, f'test_execution_{timestamp}.log')

    logger = logging.getLogger("SDET_Framework")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Cleaner format without the word "INFO" cluttering the steps
        formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO) 
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()