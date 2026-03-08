import sys
import os

# Append the parent directory to sys.path so it can import from the root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from ingestion.log_processor import load_and_split_logs_from_dir
from langchain_chroma import Chroma

def build_vector_db(directory_path='data', persist_directory='chroma_db'):
    """
    Builds a Chroma vector database from log files in a directory.

    Args:
        directory_path (str): Path to the directory containing log files.
        persist_directory (str): Directory to persist the vector database.
    """
    # Call load_and_split_logs_from_dir to get the chunks
    chunks = load_and_split_logs_from_dir(directory_path)
    
    if not chunks:
        print("No chunks were generated from the log files.")
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
    # Construct absolute path to data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    persist_dir = os.path.join(base_dir, 'chroma_db')
    
    if os.path.exists(data_dir):
        # 5.1 Call build_vector_db
        build_vector_db(data_dir, persist_directory=persist_dir)
        
        # 5.2 Instantiate the DB directly
        ai = AIService()
        db = Chroma(persist_directory=persist_dir, embedding_function=ai.get_embeddings())
        
        # 5.3 Perform a dummy search
        results = db.similarity_search('test', k=1)
        
        # 5.4 Print the metadata of the first returned document
        if results:
            print(f"Metadata of the first returned document: {results[0].metadata}")
    else:
        print(f"Directory not found: {data_dir}")