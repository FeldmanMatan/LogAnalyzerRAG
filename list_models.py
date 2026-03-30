import truststore
truststore.inject_into_ssl()

import os
import warnings

# Suppress the deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai

# 1. Load Environment Variables (Logic adapted from ai_service.py)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Manual fallback for .env if not loaded by dotenv
if not os.getenv("GOOGLE_API_KEY"):
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

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found. Please check your .env file.")
        return

    # 2. Configure the Google GenAI Client
    # Use REST transport to avoid gRPC connection issues (503)
    genai.configure(api_key=api_key, transport="rest")

    print("Fetching available models from Google API...\n")
    
    try:
        # 3. List Models
        print(f"{'Model Name':<40} | {'Supported Methods'}")
        print("-" * 90)
        for m in genai.list_models():
            # Filter for models that are likely relevant (generateContent or embedContent)
            if 'generateContent' in m.supported_generation_methods or 'embedContent' in m.supported_generation_methods:
                methods = ", ".join(m.supported_generation_methods)
                print(f"{m.name:<40} | {methods}")
        print("\nModel listing complete.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    list_models()