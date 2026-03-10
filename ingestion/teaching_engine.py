import os
import json
import sys
import sqlite3
import re

# Setup the path to ensure imports work correctly from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from langchain_chroma import Chroma
from langchain_core.documents import Document

STATS_DB_PATH = "logs_stats.db"

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

def parse_and_save_to_sqlite(lines, source_file, log_type):
    """
    Parses log lines using regex from config and saves them to SQLite.
    """
    # Construct paths relative to the root directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'log_format.json')
    db_full_path = os.path.join(base_dir, STATS_DB_PATH)

    with open(config_path, 'r') as f:
        log_formats = json.load(f)

    if log_type not in log_formats:
        raise ValueError(f"Log type '{log_type}' not found in configuration.")

    config = log_formats[log_type]
    regex_pattern = config['regex']
    columns = config['columns']

    pattern = re.compile(regex_pattern)
    conn = sqlite3.connect(db_full_path)
    cursor = conn.cursor()

    inserted_count = 0
    # Prepare INSERT statement dynamically
    placeholders = ", ".join(["?"] * (len(columns) + 1)) # +1 for source_file
    column_names = ", ".join(["source_file"] + columns)
    sql = f"INSERT INTO {log_type} ({column_names}) VALUES ({placeholders})"

    for line in lines:
        match = pattern.search(line)
        if match:
            # Combine source_file with the captured groups
            data = (source_file,) + match.groups()
            cursor.execute(sql, data)
            inserted_count += 1

    conn.commit()
    conn.close()
    return inserted_count

def teach_single(file_path, start_line, end_line, status, explanation, save_to_stats=False, log_type=None):
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
        
        msg = "Success: Knowledge added to vector store."

        # If requested, parse and save to SQLite stats DB
        if save_to_stats and log_type:
            rows = parse_and_save_to_sqlite(log_segment, file_path, log_type)
            msg += f" Also added {rows} rows to '{log_type}' table in stats DB."

        return msg

    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    load_and_teach()