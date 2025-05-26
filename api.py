from fastapi import FastAPI, HTTPException, Request, Query
from pydantic import BaseModel
from typing import List, Optional
from multi_graph_agent import ConversationAgentGraph
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multi-Agent Office Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the agent graph
agent_graph = ConversationAgentGraph.create_agent_graph()

class Message(BaseModel):
    content: str
    session_id: Optional[str] = None

class Response(BaseModel):
    content: str
    agent_name: str
    transition_path: Optional[List[str]] = None

def clean_response(response: str) -> str:
    """Clean and format the response text"""
    # Remove any transition markers from the response
    if "TRANSITION_TO:" in response:
        response = response.split("TRANSITION_TO:")[0].strip()
    
    # Remove any global context markers
    if "[Global Context:" in response:
        response = response.split("[Global Context:")[0].strip()
    
    # Remove any transition messages
    if "[Transitioning to" in response:
        response = response.split("[Transitioning to")[0].strip()
    
    # Limit to 50 words
    words = response.split()
    if len(words) > 50:
        response = " ".join(words[:50]) + "..."
    
    return response

async def process_chat_message(content: str) -> Response:
    """Process a chat message and return the response"""
    try:
        # Process the message through the agent graph
        response_chunks = []
        for chunk in agent_graph.process_message(content):
            response_chunks.append(chunk)
        
        # Combine chunks and clean the response
        full_response = "".join(response_chunks)
        cleaned_response = clean_response(full_response)
        
        # Get current agent and path
        current_agent = agent_graph.get_current_agent().get_name()
        agent_path = agent_graph.get_agent_path()
        
        return Response(
            content=cleaned_response,
            agent_name=current_agent,
            transition_path=agent_path
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
@app.post("/chat/")
async def chat_post(request: Request):
    """Handle POST requests to the chat endpoint"""
    try:
        logger.debug(f"Received POST request: {request.method} {request.url}")
        body = await request.json()
        logger.debug(f"Request body: {body}")
        message = Message(**body)
        return await process_chat_message(message.content)
    except Exception as e:
        logger.error(f"Error in POST chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat")
@app.get("/chat/")
async def chat_get(message: str = Query(..., description="The message to process")):
    """Handle GET requests to the chat endpoint"""
    try:
        logger.debug(f"Received GET request with message: {message}")
        return await process_chat_message(message)
    except Exception as e:
        logger.error(f"Error in GET chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
@app.get("/agents/")
async def get_agents():
    """Get list of all available agents"""
    return {
        "agents": [
            "reception_agent",
            "booking_agent",
            "scheduler_agent",
            "faq_agent",
            "emergency_agent",
            "feedback_agent",
            "hr_agent",
            "it_agent",
            "visitor_agent"
        ]
    }

@app.get("/current-agent")
@app.get("/current-agent/")
async def get_current_agent():
    """Get the currently active agent"""
    return {
        "agent": agent_graph.get_current_agent().get_name()
    }

# Add error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"General Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 