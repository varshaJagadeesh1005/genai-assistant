import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.agent import GenAIAgent
from backend.utils import logger, read_sample_data, format_error_response

# Load environment
load_dotenv()

app = FastAPI(
    title="GenAI Assistant API",
    description="Backend API for managing conversations and orchestrating AI agents.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI Agent
agent = GenAIAgent()

class ChatRequest(BaseModel):
    message: str
    use_context: bool = True

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.get("/api/status")
async def get_status():
    """Retrieve backend server and configuration status."""
    has_gemini = bool(os.getenv("GEMINI_API_KEY") and "your_gemini_api_key" not in os.getenv("GEMINI_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY") and "your_openai_api_key" not in os.getenv("OPENAI_API_KEY"))
    return {
        "status": "online",
        "configured_providers": {
            "gemini": has_gemini,
            "openai": has_openai
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Exposes a route to interact with the GenAI agent."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        # Load sample text file context if selected
        context = read_sample_data() if request.use_context else ""
        
        # Generate the response via Agent
        ai_response = agent.generate_response(request.message, context)
        
        return ChatResponse(response=ai_response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend files at root
frontend_dir = os.path.abspath("frontend")
if os.path.exists(frontend_dir):
    # Route for home page
    @app.get("/")
    async def serve_home():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
        
    app.mount("/", StaticFiles(directory=frontend_dir), name="frontend")
else:
    logger.warning("Frontend directory not found. Static files will not be served.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
