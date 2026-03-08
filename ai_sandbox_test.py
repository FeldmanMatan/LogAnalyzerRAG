import os
from dotenv import load_dotenv

# --- Open World Imports (Google) ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# --- Closed World Imports (Mock/Offline) ---
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.embeddings import FakeEmbeddings

def test_ai_provider(provider_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING AI PROVIDER: {provider_name.upper()}")
    print(f"{'='*60}")

    # 1. Initialization Phase
    if provider_name == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ Error: GOOGLE_API_KEY is missing in .env file.")
            return

        print("[1] Initializing Open World (Google Gemini)...")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    elif provider_name == "enterprise_mock":
        print("[1] Initializing Closed World (Offline Enterprise Mock)...")
        # Simulating an offline LLM that returns a static response
        llm = FakeListChatModel(responses=["[SECURE OFFLINE AI] Hello! I analyzed the local log and found no errors."])
        # Simulating an offline embedding model (creates dummy vectors of size 768)
        embeddings = FakeEmbeddings(size=768)

    else:
        print(f"❌ Error: Unknown provider '{provider_name}'")
        return

    # 2. Testing Chat Generation (LLM)
    print("\n[2] Testing Chat Generation (LLM)...")
    try:
        prompt = "Analyze this system log for errors."
        print(f"    User Prompt: '{prompt}'")
        response = llm.invoke(prompt)
        print(f"    🤖 AI Response: {response.content}")
        print("    ✅ Chat Test: PASS")
    except Exception as e:
        print(f"    ❌ Chat Test: FAIL - {e}")

    # 3. Testing Vector Generation (Embeddings for DB)
    print("\n[3] Testing Vector Generation (Embeddings)...")
    try:
        text_to_embed = "Memory leak detected at line 42"
        vector = embeddings.embed_query(text_to_embed)
        print(f"    Text to embed: '{text_to_embed}'")
        print(f"    🔢 Generated Vector: List of {len(vector)} numbers (e.g., {vector[0]:.4f}, {vector[1]:.4f}...)")
        print("    ✅ Embeddings Test: PASS")
    except Exception as e:
        print(f"    ❌ Embeddings Test: FAIL - {e}")

    print(f"\n🏁 Finished testing {provider_name.upper()}")

if __name__ == "__main__":
    load_dotenv() # Load variables from .env
    
    while True:
        print("\n" + "*"*40)
        print("🌐 AI ENVIRONMENT SANDBOX TESTER")
        print("*"*40)
        print("1. Test 'Open World' (Google Gemini)")
        print("2. Test 'Closed World' (Enterprise Mock/Offline)")
        print("0. Exit")
        
        choice = input("\nSelect an option (0-2): ")
        
        if choice == '1':
            test_ai_provider("gemini")
        elif choice == '2':
            test_ai_provider("enterprise_mock")
        elif choice == '0':
            print("Exiting Sandbox.")
            break
        else:
            print("Invalid choice. Try again.")