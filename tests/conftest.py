import pytest
import os
from tests.utils.test_logger import logger

# Global accumulator for the final execution report
test_results = []

def get_suite_category(nodeid: str) -> str:
    """Classifies tests into categories based on their file path or name."""
    if "integration" in nodeid: return "Integration Tests"
    if "visual_e2e" in nodeid: return "Visual UI Tests"
    if "langgraph" in nodeid: return "AI E2E Tests"
    return "General Tests"

@pytest.fixture(scope="session", autouse=True)
def global_test_setup():
    logger.info("="*60)
    logger.info("🚀 STARTING AUTOMATION TEST EXECUTION")
    
    mock_mode = os.environ.get("USE_MOCK_LLM", "false")
    logger.info(f"🌍 Global Environment: USE_MOCK_LLM = {mock_mode}")
    
    if mock_mode == "false" and "GOOGLE_API_KEY" not in os.environ:
        logger.error("CRITICAL: GOOGLE_API_KEY environment variable is missing!")
        pytest.exit("Aborting: E2E tests require a GOOGLE_API_KEY.")
        
    logger.info("="*60 + "\n")
    yield 

# --- AUTOMATIC TEST ANNOUNCEMENTS ---

def pytest_runtest_setup(item):
    """Fires automatically exactly before a test starts."""
    suite = get_suite_category(item.nodeid)
    logger.info(f"\n{'='*50}")
    logger.info(f"🧪 RUNNING TEST: {item.name}")
    logger.info(f"📁 SUITE:        {suite}")
    logger.info(f"{'-'*50}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Captures the pass/fail status and logs it immediately."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call": 
        status = rep.outcome.upper()
        suite = get_suite_category(item.nodeid)
        
        # Save for the final summary table
        test_results.append({
            "name": item.name,
            "suite": suite,
            "status": status,
            "duration": f"{rep.duration:.2f}s"
        })

        # Log the conclusion of the specific test
        if status == "PASSED":
            logger.info(f"✅ TEST PASSED: {item.name}")
        elif status == "FAILED":
            logger.error(f"❌ TEST FAILED: {item.name}")
        else:
            logger.warning(f"⏭️ TEST SKIPPED: {item.name}")
        logger.info(f"{'='*50}\n")

# --- CATEGORIZED FINAL REPORT ---

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generates the final Summary Table grouped by Test Categories."""
    logger.info("\n\n" + "#"*70)
    logger.info("📊 AUTOMATION EXECUTION SUMMARY")
    logger.info("#"*70)
    
    # Group results by suite category
    grouped_results = {}
    for res in test_results:
        grouped_results.setdefault(res["suite"], []).append(res)
        
    # Print grouped tables
    for suite, results in grouped_results.items():
        logger.info(f"\n📌 CATEGORY: {suite.upper()}")
        logger.info(f"{'TEST NAME'.ljust(45)} | {'STATUS'.ljust(8)} | {'TIME'}")
        logger.info("-" * 65)
        
        for res in results:
            status_icon = "✅ PASS" if res["status"] == "PASSED" else "❌ FAIL" if res["status"] == "FAILED" else "⏭️ SKIP"
            # Format the name to not overflow
            display_name = (res['name'][:42] + '...') if len(res['name']) > 45 else res['name']
            logger.info(f"{display_name.ljust(45)} | {status_icon.ljust(8)} | {res['duration']}")
            
    logger.info("\n" + "#"*70 + "\n")