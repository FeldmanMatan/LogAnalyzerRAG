import sys
import os

# Append the parent directory to sys.path so it can import from the root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from langchain_chroma import Chroma

def get_standard_logs(query, db_directory='chroma_db', k=5):
    """
    Retrieves standard logs matching the query.
    """
    # Instantiate AIService and get the embeddings model
    ai = AIService()
    embeddings = ai.get_embeddings()

    # Load the Chroma database
    db = Chroma(persist_directory=db_directory, embedding_function=embeddings)

    # Perform a search using db.similarity_search with filter
    results = db.similarity_search(query, k=k, filter={'status': 'standard'})

    # Return a formatted string combining the page_content and metadata['source']
    formatted_results = []
    for doc in results:
        source = doc.metadata.get('source', 'Unknown')
        formatted_results.append(f"Source: {source}\nContent: {doc.page_content}")
    
    return "\n\n".join(formatted_results)

def get_golden_logs(query, db_directory='chroma_db', k=5):
    """
    Retrieves golden logs matching the query.
    """
    # Instantiate AIService and get the embeddings model
    ai = AIService()
    embeddings = ai.get_embeddings()

    # Load the Chroma database
    db = Chroma(persist_directory=db_directory, embedding_function=embeddings)

    # Perform a search using db.similarity_search with filter
    results = db.similarity_search(query, k=k, filter={'status': 'golden'})

    # Return a formatted string combining the page_content and metadata['source']
    formatted_results = []
    for doc in results:
        source = doc.metadata.get('source', 'Unknown')
        formatted_results.append(f"Source: {source}\nContent: {doc.page_content}")
    
    return "\n\n".join(formatted_results)

if __name__ == '__main__':
    # Acceptance Test
    test_query = 'memory'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, 'chroma_db')

    print('--- Golden Logs ---')
    print(get_golden_logs(test_query, db_directory=db_dir))

    print('\n--- Standard Logs ---')
    print(get_standard_logs(test_query, db_directory=db_dir))