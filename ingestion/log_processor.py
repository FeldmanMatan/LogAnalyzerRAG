import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split_log(file_path):
    """
    Loads a log file and splits it into chunks using LangChain.

    Args:
        file_path (str): Path to the log file.

    Returns:
        list: List of split document chunks.
    """
    # Load the log file using TextLoader
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    # Initialize the splitter with chunk_size=100 and chunk_overlap=20
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )

    # Split the documents into chunks
    chunks = text_splitter.split_documents(documents)
    return chunks

if __name__ == "__main__":
    # Construct the absolute path to the sample log file
    # Assumes structure: project_root/ingestion/log_processor.py and project_root/data/sample.log
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_log_path = os.path.join(base_dir, "data", "sample.log")

    if os.path.exists(sample_log_path):
        chunks = load_and_split_log(sample_log_path)
        print(f"Number of chunks created: {len(chunks)}")
        if chunks:
            print(f"Text of the first chunk:\n{chunks[0].page_content}")
    else:
        print(f"File not found: {sample_log_path}")