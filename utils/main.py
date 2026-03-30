from ai_service import AIService

def test_connection():
    """
    Tests the connection to the Gemini API using the AIService wrapper.
    """
    print("Initializing AI Service...")
    try:
        # Instantiate the AI wrapper
        ai = AIService()
        
        # Get the configured LLM object
        llm = ai.get_llm()
        
        print("Sending test prompt to Gemini...")
        
        # Send a simple message to verify connectivity
        response = llm.invoke("Hello, connection test! Please reply with a short greeting.")
        
        # Print the response content to the console
        print("\n--- Response from AI ---")
        print(response.content)
        print("------------------------\n")
        print("Success: Infrastructure is ready!")
        
    except Exception as e:
        print(f"\nError connecting to AI service: {e}")
        print("Please check your network and .env file.")

# This is the crucial block that actually RUNS the function
if __name__ == "__main__":
    test_connection()