from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests  # Bypass the outdated library entirely

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# IMPORTANT: Put your real API key from Google AI Studio inside the quotes below!
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        # Direct API URL for Gemini 1.5 Flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # Set up system instructions and user message structure for the API call
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": req.message}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": (
                            "You are CareerPilot AI, a smart and helpful career counseling chatbot. "
                            "Answer ANY questions regarding careers, courses, degrees (like MBBS, engineering), "
                            "jobs, or future student planning. Keep responses professional, clear, and scannable."
                        )
                    }
                ]
            }
        }
        
        # Make the network request directly to Google
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        # Extract the reply text from Google's standard JSON response template
        reply = response_data['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        reply = "I ran into a connection issue with my AI brain. Please double-check your API key and try again!"

    return {"reply": reply}