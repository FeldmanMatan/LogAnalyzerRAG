import sys
import os

# Append the parent directory to sys.path to allow imports from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import StateGraph, START, END
from agents.state import AgentState
from agents.baseline_specialist import baseline_node
from agents.investigator_agent import investigator_node

def build_team_graph(memory=None):
    """
    Constructs the multi-agent workflow graph with persistent memory.
    
    The flow is sequential:
    START -> Baseline Specialist -> Investigator Agent -> END
    """
    # Initialize the graph with the shared state schema
    workflow = StateGraph(AgentState)

    # Add the specialist nodes
    workflow.add_node("Baseline_Specialist", baseline_node)
    workflow.add_node("Investigator_Agent", investigator_node)

    # Define the edges to control the flow
    workflow.add_edge(START, "Baseline_Specialist")
    workflow.add_edge("Baseline_Specialist", "Investigator_Agent")
    workflow.add_edge("Investigator_Agent", END)

    # Compile the graph into an executable application, attaching the checkpointer
    app = workflow.compile(checkpointer=memory)
    return app