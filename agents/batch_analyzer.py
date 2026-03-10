import sys
import os
import concurrent.futures

# Append the parent directory to sys.path to allow imports from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.state import AgentState
from agents.baseline_specialist import baseline_node
from agents.investigator_agent import investigator_node
from langchain_core.messages import HumanMessage
from ai_service import AIService

def analyze_log_file_in_batches(file_path: str, chunk_size: int = 50) -> str:
    """
    Analyzes a large log file by splitting it into chunks, processing them in parallel
    against the baseline, and synthesizing the results (Map-Reduce).

    Args:
        file_path (str): Path to the log file.
        chunk_size (int): Number of lines per chunk.

    Returns:
        str: A synthesized executive summary of the findings.
    """
    print(f"--- Starting Batch Analysis for: {file_path} ---")

    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    try:
        # Step 1: Get Baseline Profile
        print("--- Step 1: Retrieving Baseline Profile ---")
        # Create a dummy state to trigger the baseline node
        initial_state: AgentState = {
            "messages": [],
            "baseline_profile": "",
            "investigation_report": "",
            "next_node": ""
        }
        baseline_result = baseline_node(initial_state)
        baseline_profile = baseline_result.get("baseline_profile", "No baseline available.")

        # Step 2: Read and Chunk the File
        print(f"--- Step 2: Reading and Chunking File (Chunk Size: {chunk_size}) ---")
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        if not lines:
            return "The log file is empty."

        chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
        print(f"Created {len(chunks)} chunks.")

        # Step 3: Define Map Function (Process Chunk)
        def process_chunk(args):
            chunk_index, chunk_lines = args
            joined_lines = "".join(chunk_lines)
            
            prompt = (
                "Analyze this specific log chunk against the baseline to find anomalies. "
                "Focus only on actual errors or deviations.\n"
                f"Log Chunk:\n{joined_lines}"
            )
            
            # Create local state for this chunk
            local_state: AgentState = {
                "messages": [HumanMessage(content=prompt)],
                "baseline_profile": baseline_profile,
                "investigation_report": "",
                "next_node": ""
            }
            
            # Run investigator node
            result = investigator_node(local_state)
            return (chunk_index, result.get("investigation_report", ""))

        # Step 4: Parallel Execution (Map)
        print("--- Step 4: Processing Chunks in Parallel ---")
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Map process_chunk over enumerated chunks
            results = list(executor.map(process_chunk, enumerate(chunks)))

        # Step 5: Reduce/Synthesis
        print("--- Step 5: Synthesizing Results ---")
        # Sort by index to keep log order
        results.sort(key=lambda x: x[0])
        
        all_reports = "\n\n".join([f"--- Chunk {idx} ---\n{report}" for idx, report in results])
        
        ai = AIService()
        llm = ai.get_llm()
        synthesis_prompt = f"Synthesize these individual log chunk reports into one cohesive, executive summary of anomalies:\n\n{all_reports}"
        
        final_response = llm.invoke(synthesis_prompt)
        return final_response.content

    except Exception as e:
        return f"Error during batch analysis: {str(e)}"