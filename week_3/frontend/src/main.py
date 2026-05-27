import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

BACKEND_URL = os.getenv("BACKEND_URL")
if not BACKEND_URL:
    parent_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=parent_env_path)
    BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    raise RuntimeError("❌ 'BACKEND_URL' environment variable is missing.")

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat_page.html",
        context={"message": "hello from frontend!"},
    )

@app.post("/submit-chat")
async def handle_ui_submission(user_message: str = Form(""), chat_file: UploadFile = File(None)):
    if not chat_file:
        return JSONResponse(status_code=400, content={"error": "Please attach your resume file."})

    # Read binary bytes from the frontend multi-part context stream
    file_bytes = await chat_file.read()
    
    # Bundle data fields explicitly for network serialization forwarding
    files = {"chat_file": (chat_file.filename, file_bytes, chat_file.content_type)}
    data = {"user_message": user_message}

    async with httpx.AsyncClient() as client:
        try:
            # Relay request over to the standalone Python backend instance
            response = await client.post(BACKEND_URL, files=files, data=data, timeout=None)
            
            # Forward backend's SkillGapResult response dictionary right back to your JS agent
            return JSONResponse(content=response.json(), status_code=response.status_code)
            
        except httpx.ConnectError:
            return JSONResponse(
                status_code=503, 
                content={"error": "Backend microservice unreachable. Verify port 8000 configuration status."}
            )
        except httpx.ReadTimeout:
            return JSONResponse(
                status_code=504,
                content={"error": "The AI model took too long to respond. Please try again."}
            )
