from langchain_ollama import ChatOllama
import os

def get_llm():
    # Make sure Ollama exposes "llama3" or "llama" (adjust max tokens if needed)
    return ChatOllama(model="llama3.2:latest", temperature=0)

def get_json_llm():
    return ChatOllama(model="llama3.2:latest", temperature=0, format="json")
