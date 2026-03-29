import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.investigator_agent import investigator_node
from langchain_core.messages import HumanMessage

print("Testing Investigator Agent...")

# Mocking the baseline and the user query
dummy_baseline = "Rule 1: Normal system operation involves only INFO logs. Any ERROR is an anomaly."
dummy_state = {
    "messages": [HumanMessage(content="How many logs do we have in app_logs, and do they violate the baseline?")],
    "baseline_profile": dummy_baseline,
    "investigation_report": "",
    "next_node": ""
}

try:
    result = investigator_node(dummy_state)
    print("\n--- Investigation Report ---")
    print(result.get("investigation_report", "No report generated."))
    print("----------------------------")
except Exception as e:
    print(f"Error during execution: {e}")