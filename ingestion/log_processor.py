import os
import glob
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_single_file(file_path):
    try:
        # Load the file using TextLoader and split it using RecursiveCharacterTextSplitter
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
        chunks = text_splitter.split_documents(documents)
        
        # Get the base filename
        filename = os.path.basename(file_path)
        
        # Iterate through the chunks and update metadata
        for chunk in chunks:
            if 'golden' in filename.lower():
                chunk.metadata.update({'status': 'golden', 'source': filename})
            else:
                chunk.metadata.update({'status': 'standard', 'source': filename})
        
        return chunks
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

def load_and_split_logs_from_dir(directory_path):
    # Use glob to find all .log files in the given directory
    log_files = glob.glob(os.path.join(directory_path, "*.log"))
    
    # Use ThreadPoolExecutor to run process_single_file concurrently
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_single_file, log_files)
        
    # Flatten the list of lists into a single flat list of chunks
    flat_chunks = []
    for result in results:
        flat_chunks.extend(result)
        
    return flat_chunks

if __name__ == "__main__":
    # Construct the absolute path to the data directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")

    if os.path.exists(data_dir):
        chunks = load_and_split_logs_from_dir(data_dir)
        print(f"Total number of chunks created: {len(chunks)}")
        if chunks:
            print(f"Metadata of the first chunk: {chunks[0].metadata}")
            print(f"Metadata of the last chunk: {chunks[-1].metadata}")
    else:
        print(f"Directory not found: {data_dir}")