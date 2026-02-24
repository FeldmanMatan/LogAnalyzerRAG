try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    # Optional dependency; continue if not available
    pass

import os

# Prefer python-dotenv if available, otherwise fall back to a simple .env parser
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

class AIService:
    """
    This class wraps the AI provider logic.
    It isolates provider-specific logic to allow easy swapping of LLMs in the future.
    """

    def __init__(self):
        # Retrieve the API key from the environment
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")

        # Initialize the Embedding model (Used for Stage A & B)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=self.api_key
        )

        # Initialize the Generation model (LLM) (Used for Stage C)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=self.api_key,
            temperature=0
        )

    def get_embeddings(self):
        """Returns the configured embedding model."""
        return self.embeddings

    def get_llm(self):
        """Returns the configured LLM."""
        return self.llm
