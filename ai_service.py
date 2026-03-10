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
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings

class AIService:
    """
    This class wraps the AI provider logic.
    It isolates provider-specific logic to allow easy swapping of LLMs in the future.
    Implements a Factory Pattern based on the AI_PROVIDER environment variable.
    """

    def __init__(self):
        # Determine the AI provider (default to 'gemini')
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        
        # Retrieve the API key from the environment
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        # Validate API key only if using Gemini
        if self.provider == 'gemini' and not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")

    def get_embeddings(self):
        """Returns the configured embedding model based on the provider."""
        if self.provider == 'gemini':
            return GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001",
                google_api_key=self.api_key
            )
        elif self.provider == 'ollama':
            return OllamaEmbeddings(
                model="llama3",
                base_url="http://localhost:11434"
            )
        else:
            raise ValueError(f"Unsupported AI_PROVIDER: {self.provider}")

    def get_llm(self):
        """Returns the configured LLM based on the provider."""
        if self.provider == 'gemini':
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=self.api_key,
                temperature=0
            )
        elif self.provider == 'ollama':
            return ChatOllama(
                model="llama3",
                base_url="http://localhost:11434",
                temperature=0
            )
        else:
            raise ValueError(f"Unsupported AI_PROVIDER: {self.provider}")
