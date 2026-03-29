from agents.state import AgentState
from agents.baseline_specialist import baseline_node

print("Testing Baseline Specialist...")
# Create an empty initial state
dummy_state = AgentState(messages=[], baseline_profile="", investigation_report="", next_node="")

# Run the node manually
result = baseline_node(dummy_state)

print("\n--- Generated Baseline Profile ---")
print(result.get("baseline_profile", "Failed to generate profile"))
print("----------------------------------")