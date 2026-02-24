import sys
import os

# Append the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_service import AIService
from retrieval.retriever import get_relevant_logs
from langchain_core.prompts import PromptTemplate

def ask_log_analyzer(query):
    """
    Analyzes logs using RAG to answer a user query.

    Args:
        query (str): The user's question.

    Returns:
        str: The answer from the LLM.
    """
    # Call get_relevant_logs(query, k=5) and extract the page_content
    docs = get_relevant_logs(query, k=5)
    context = "\n".join([doc.page_content for doc in docs])

    # Create a PromptTemplate
    template = 'You are a senior DevOps engineer analyzing system logs. Based ONLY on the following context, answer the user question. Context: {context} Question: {question} Answer:'
    prompt = PromptTemplate(template=template, input_variables=['context', 'question'])

    # Instantiate AIService and get the LLM
    ai = AIService()
    llm = ai.get_llm()

    # Create a chain: prompt | llm
    chain = prompt | llm

    # Invoke the chain with context and question
    response = chain.invoke({'context': context, 'question': query})
    return response.content

if __name__ == '__main__':
    test_query = 'Why did the database connection fail and at what time?'
    answer = ask_log_analyzer(test_query)
    print(answer)