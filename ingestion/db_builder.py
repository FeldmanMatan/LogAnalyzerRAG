import sys
import os

# Append the parent directory to sys.path so it can import from the root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from ingestion.log_processor import load_and_split_log
from langchain_chroma import Chroma

def build_vector_db(file_path, persist_directory='db'):
    """
    Builds a Chroma vector database from a log file.

    Args:
        file_path (str): Path to the log file.
        persist_directory (str): Directory to persist the vector database.
    """
    # Call load_and_split_log to get the chunks
    chunks = load_and_split_log(file_path)
    
    if not chunks:
        print("No chunks were generated from the log file.")
        return

    # Instantiate AIService and get the embeddings model
    try:
        ai = AIService()
        embeddings = ai.get_embeddings()
    except Exception as e:
        print(f"Error initializing AI Service: {e}")
        return

    # Create and persist a Chroma vector store
    print(f"Creating vector store in '{persist_directory}'...")
    Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_directory)

    # Print a success message with the number of vectors stored
    print(f"Success! {len(chunks)} vectors stored in '{persist_directory}'.")

if __name__ == '__main__':
    # Construct absolute path to data/sample.log
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_log_path = os.path.join(base_dir, 'data', 'sample.log')
    
    if os.path.exists(sample_log_path):
        # Persist the DB in a 'chroma_db' folder in the project root
        build_vector_db(sample_log_path, persist_directory=os.path.join(base_dir, 'chroma_db'))
    else:
        print(f"File not found: {sample_log_path}")