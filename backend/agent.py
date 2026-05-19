import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

from backend.utils import logger

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# LLM setup using LangChain
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        google_api_key=api_key
    )
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    llm = None

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful GenAI assistant. Be concise. Context: {context}"),
    ("human", "{question}")
])

# Chain definition (LCEL)
if llm:
    chain = prompt | llm | StrOutputParser()
else:
    chain = None

def ask(question: str, context: str = "") -> str:
    """Invokes the LangChain generation process."""
    if chain is None:
        return "⚠️ Offline Fallback Mode: Please configure a valid GOOGLE_API_KEY in the `.env` file."
    
    try:
        return chain.invoke({"question": question, "context": context})
    except Exception as e:
        logger.error(f"Error invoking chain: {e}")
        return f"Error: {e}"
