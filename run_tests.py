import argparse
import sys
import pytest
import os

def main():
    # 1. Define CLI arguments
    parser = argparse.ArgumentParser(description="LogAnalyzer Master Test Runner")
    parser.add_argument(
        '--suite', 
        choices=['all', 'integration', 'e2e', 'visual'], 
        default='all',
        help='Which test suite to run? (all, integration, e2e, visual)'
    )
    args = parser.parse_args()

    # 2. Print Execution Banner
    print("\n" + "="*60)
    print("🚀 Starting LogAnalyzer Test Automation Framework...")
    print(f"📁 Target Suite: {args.suite.upper()}")
    print("="*60 + "\n")

    # 3. Environment Variables Configuration
    os.environ["IS_TEST_ENV"] = "true"
    
    # For integration tests, use a Mock LLM to save Google API costs/quota
    if args.suite == "integration":
        os.environ["USE_MOCK_LLM"] = "true"
    else:
        os.environ["USE_MOCK_LLM"] = "false"

    # 4. Smart Routing based on user selection
    test_paths = {
        'all': ['tests/'],
        'integration': ['tests/integration/'],
        'e2e': ['tests/e2e/test_langgraph_ddt.py'],
        'visual': ['tests/e2e/test_visual_e2e.py']
    }

    # Construct PyTest command (-v for verbose, --tb=short for cleaner error traces)
    pytest_args = ["-v", "--tb=short"] + test_paths[args.suite]

    # 5. Execute PyTest
    exit_code = pytest.main(pytest_args)
    
    # 6. Print Final Status
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ All target tests passed successfully!")
    else:
        print(f"❌ Tests finished with failed cases (Exit Code: {exit_code})")
    print("="*60 + "\n")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()