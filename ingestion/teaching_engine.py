import os
import json
import sys

# Setup the path to ensure imports work correctly from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from langchain_chroma import Chroma
from langchain_core.documents import Document

def load_and_teach(config_path='teaching_config.json'):
    # Load the JSON file
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{config_path}'.")
        return

    # Initialize AIService and embeddings
    ai = AIService()
    embeddings = ai.get_embeddings()

    # Initialize Chroma vectorstore
    vectorstore = Chroma(persist_directory='./chroma_db', embedding_function=embeddings)

    # Initialize an empty list docs
    docs = []

    # Loop through each entry in the JSON
    for entry in config:
        try:
            file_path = entry['file_path']
            start_line = entry['start_line']
            end_line = entry['end_line']

            # Read the file specified
            with open(file_path, 'r', encoding='utf-8', errors='replace') as log_file:
                lines = log_file.readlines()

            # Extract lines (handle 1-based indexing)
            # Python lists are 0-indexed, so start_line 1 becomes index 0
            log_segment = lines[start_line - 1 : end_line]
            log_text = "".join(log_segment)

            # Create a Document object
            doc = Document(
                page_content=log_text,
                metadata={"source": file_path, "status": entry['status'], "human_explanation": entry['explanation']}
            )

            # Append to docs
            docs.append(doc)
            print(f"Successfully processed entry: {file_path} (Lines {start_line}-{end_line})")

        except FileNotFoundError:
            print(f"Error: File '{entry.get('file_path')}' not found.")
        except Exception as e:
            print(f"Error processing entry: {e}")

    # Insert them into the DB
    if docs:
        vectorstore.add_documents(docs)
        print(f"Finished adding {len(docs)} documents to the vector store.")

def teach_single(file_path, start_line, end_line, status, explanation):
    """
    Ingests a single log segment into the vector store based on user input.
    """
    try:
        # Initialize AIService and embeddings
        ai = AIService()
        embeddings = ai.get_embeddings()

        # Initialize Chroma vectorstore
        vectorstore = Chroma(persist_directory='./chroma_db', embedding_function=embeddings)

        # Read the file specified
        with open(file_path, 'r', encoding='utf-8', errors='replace') as log_file:
            lines = log_file.readlines()

        # Extract lines (handle 1-based indexing)
        log_segment = lines[start_line - 1 : end_line]
        log_text = "".join(log_segment)

        # Create a Document object
        doc = Document(
            page_content=log_text,
            metadata={"source": file_path, "status": status, "human_explanation": explanation}
        )

        # Insert into DB
        vectorstore.add_documents([doc])
        return "Success: Knowledge added to vector store."

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    load_and_teach()