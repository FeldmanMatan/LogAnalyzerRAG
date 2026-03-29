import sys
import os

# Insert the root directory at the BEGINNING of sys.path (index 0) 
# to prioritize local modules over installed pip packages.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from agents.supervisor import build_team_graph

print("Testing the full Multi-Agent Team (Supervisor Workflow)...")

# Build the workflow graph
app = build_team_graph()

# Initial state with a user query
initial_state = {
    "messages": [HumanMessage(content="Analyze the app_logs statistics and tell me if they violate the normal baseline.")],
    "baseline_profile": "",
    "investigation_report": "",
    "next_node": ""
}

# Run the graph
final_state = app.invoke(initial_state)

print("\n=== FINAL INVESTIGATION REPORT ===")
print(final_state.get("investigation_report", "No report generated."))
print("==================================")