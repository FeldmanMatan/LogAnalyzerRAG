import sys
import os

# Append the parent directory to sys.path so it can import from the root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from langchain_chroma import Chroma

def get_relevant_logs(query, db_directory='chroma_db', k=5):
    """
    Retrieves relevant log chunks from the Chroma vector database.

    Args:
        query (str): The search query.
        db_directory (str): Path to the Chroma database directory.
        k (int): Number of documents to retrieve.

    Returns:
        list: List of relevant documents.
    """
    # Instantiate AIService and get the embeddings model
    ai = AIService()
    embeddings = ai.get_embeddings()

    # Resolve db_directory relative to project root if it doesn't exist locally
    if not os.path.exists(db_directory):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        potential_path = os.path.join(base_dir, db_directory)
        if os.path.exists(potential_path):
            db_directory = potential_path

    # Load the existing Chroma database from db_directory using the embedding function
    db = Chroma(persist_directory=db_directory, embedding_function=embeddings)

    # Use db.similarity_search(query, k=k) to find and return the top k relevant documents
    return db.similarity_search(query, k=k)

if __name__ == '__main__':
    # Define a test query
    test_query = 'What happened at 09:10?'

    # Call get_relevant_logs and print the page_content of the retrieved chunks
    results = get_relevant_logs(test_query)
    for doc in results:
        print(doc.page_content)