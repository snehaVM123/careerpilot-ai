import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import Groq
import uvicorn

# Initialize FastAPI
app = FastAPI(title="Career Guidance Chatbot API")

# Setup HTML templates directory
templates = Jinja2Templates(directory="templates")

# Initialize Groq Client
# Ensure you set the GROQ_API_KEY environment variable in your system or VS Code launch settings.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    # Fallback placeholder for testing; replace with your actual key if not using env vars

client = Groq(api_key=GROQ_API_KEY)

# Pydantic schema for structured API requests and easy Postman testing
class ChatRequest(BaseModel):
    message:str

# 1. Serve the Frontend Webpage
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 2. Chat API Endpoint
@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Requesting Groq Llama 3 for fast, intelligent text generation
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an encouraging, empathetic, and highly knowledgeable career counselor. "
                        "Your goal is to guide users through career choices, resume tips, skill development, "
                        "and interview prep. Keep answers structural, actionable, and warm."
                    )
                },
                {
                    "role": "user",
                    "content": payload.message
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1024
        )
        
        bot_response = chat_completion.choices[0].message.content
        return {"response": bot_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API Error: {str(e)}")

# Programmatic Uvicorn execution block
if __name__ == "__main__":
    print("Starting Career Chatbot server on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)