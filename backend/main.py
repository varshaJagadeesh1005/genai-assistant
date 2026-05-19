import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from backend.agent import ask
from backend.utils import logger, read_sample_data

# Load environment
load_dotenv()

app = FastAPI(
    title="GenAI Assistant API",
    description="Backend API powered by LangChain and Google Gemini",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class ChatRequest(BaseModel):
    message: str
    use_context: bool = True

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.get("/api/status")
async def get_status():
    has_gemini = bool(os.getenv("GOOGLE_API_KEY"))
    return {
        "status": "online",
        "configured_providers": {
            "gemini": has_gemini
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Exposes a route to interact with the GenAI agent."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
        
    try:
        context = read_sample_data() if request.use_context else ""
        # Invoke the LangChain based ask() function
        ai_response = ask(request.message, context=context)
        return ChatResponse(response=ai_response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Provide the exact /ask route from the tutorial for direct testing
class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_ai(query: Query):
    """Direct implementation of the tutorial endpoint."""
    answer = ask(query.question)
    return {"answer": answer}

# Mount frontend files at root
frontend_dir = os.path.abspath("frontend")
if os.path.exists(frontend_dir):
    @app.get("/")
    async def serve_home():
        return FileResponse(os.path.join(frontend_dir, "index.html"))
        
    app.mount("/", StaticFiles(directory=frontend_dir), name="frontend")
else:
    logger.warning("Frontend directory not found.")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
