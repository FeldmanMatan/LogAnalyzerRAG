import sys
import os

# Append the parent directory to sys.path to allow imports from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.state import AgentState
from langchain_core.messages import SystemMessage
from ai_service import AIService
from langchain_chroma import Chroma

def baseline_node(state: AgentState) -> dict:
    """
    Analyzes the 'golden' logs to create a profile of normal system behavior.
    This profile serves as a rulebook for the Investigator Agent.

    Args:
        state (AgentState): The current state of the agent graph.

    Returns:
        dict: A dictionary with the updated baseline_profile.
    """
    print("---Executing Baseline Specialist Node---")
    
    try:
        # Initialize AI Service and ChromaDB
        ai = AIService()
        llm = ai.get_llm()
        embeddings = ai.get_embeddings()
        
        # Construct path to the vector database
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        persist_dir = os.path.join(base_dir, 'chroma_db')
        
        if not os.path.exists(persist_dir):
            return {"baseline_profile": "Error: ChromaDB directory not found. Please build the database first."}

        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

        # Retrieve all documents with 'status: golden' using a metadata filter
        golden_docs = vectorstore.get(where={"status": "golden"})

        if not golden_docs or not golden_docs.get('documents'):
            print("No golden logs found in the database.")
            return {"baseline_profile": "No baseline data available."}

        # Format the retrieved data for the LLM, including human explanations
        formatted_data = []
        for i, doc_content in enumerate(golden_docs['documents']):
            metadata = golden_docs['metadatas'][i]
            explanation = metadata.get('human_explanation', 'N/A')
            formatted_data.append(f"Log Entry:\n```\n{doc_content}\n```\nHuman Explanation: {explanation}\n---")
        golden_data_str = "\n".join(formatted_data)

        # Construct the prompt for the LLM
        prompt_messages = [
            SystemMessage(content="You are a Baseline Specialist. Analyze these normal ('golden') logs and their explanations to create a concise, structured rulebook of expected system behavior."),
            ("user", f"Logs: {golden_data_str}")
        ]

        # Invoke the LLM to generate the baseline profile
        response = llm.invoke(prompt_messages)
        return {"baseline_profile": response.content}

    except Exception as e:
        return {"baseline_profile": f"Error in Baseline Specialist node: {str(e)}"}