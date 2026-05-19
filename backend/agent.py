import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
from backend.prompts import SYSTEM_PROMPT
from backend.utils import logger

# Load environment variables
load_dotenv()

class GenAIAgent:
    def __init__(self):
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Configure Gemini if key is provided
        if self.gemini_api_key and "your_gemini_api_key" not in self.gemini_api_key:
            logger.info("Initializing Google Gemini client...")
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.gemini_model = None
            
        # Configure OpenAI if key is provided
        if self.openai_api_key and "your_openai_api_key" not in self.openai_api_key:
            logger.info("Initializing OpenAI client...")
            self.openai_client = OpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None

    def generate_response(self, query: str, context: str = "") -> str:
        """
        Generates a response using Gemini, falling back to OpenAI, and then to a smart mock response
        if no API keys are configured yet.
        """
        prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Query: {query}\n\nAssistant Response:"
        
        # 1. Try Gemini
        if self.gemini_model:
            try:
                logger.info("Generating response with Gemini...")
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini API error: {e}")
                
        # 2. Try OpenAI (Fallback)
        if self.openai_client:
            try:
                logger.info("Generating response with OpenAI...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Context: {context}\n\nQuery: {query}"}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                
        # 3. Smart local fallback if no active API keys are found
        logger.warning("No active API keys found or APIs failed. Falling back to local offline responder.")
        return self._local_fallback_response(query, context)

    def _local_fallback_response(self, query: str, context: str) -> str:
        query_lower = query.lower()
        if "hello" in query_lower or "hi" in query_lower:
            return "👋 Hello! I am your local offline fallback agent. Please configure a valid API key in your `.env` file to unlock full generative AI capabilities!"
        elif "context" in query_lower or "sample" in query_lower or "data" in query_lower:
            if context:
                return f"🔍 Here is the data I found in the knowledge base:\n\n{context}"
            else:
                return "📂 No context or knowledge base text was loaded."
        else:
            return (
                "🤖 **Offline Mode Active**\n\n"
                "I received your query: *" + query + "*\n\n"
                "To get real generative answers, please edit the `.env` file in the root directory "
                "and replace the placeholder with a valid API key (e.g., `GOOGLE_API_KEY`)."
            )
