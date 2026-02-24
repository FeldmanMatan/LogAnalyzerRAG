# Simple script to verify installations
try:
    import langchain_google_genai
    import chromadb
    import dotenv
    print("Success: All packages are installed and reachable!")
except ImportError as e:
    print(f"Error: Module not found. {e}")