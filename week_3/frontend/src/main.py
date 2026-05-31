import os
import io
import httpx
from pathlib import Path
from dotenv import load_dotenv
from pypdf import PdfReader

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

MODEL_NAME = os.getenv("DEFAULT_MODEL")
if not MODEL_NAME:
    parent_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=parent_env_path)
    MODEL_NAME = os.getenv("DEFAULT_MODEL")

if not MODEL_NAME:
    raise RuntimeError("❌ 'MODEL_NAME' environment variable is missing.")

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
async def handle_ui_submission(
    user_message: str = Form(""), chat_file: UploadFile = File(None)
):

    if not user_message.strip() and not chat_file:
        return JSONResponse(
            status_code=400, content={"error": "Your message cannot be empty."}
        )

    # Read binary bytes from the frontend multi-part context stream
    extracted_text = ""

    # if the file uploaded is PDF, convert to text
    if chat_file and chat_file.filename.strip():
        file_bytes = await chat_file.read()
        if (
            chat_file.filename.lower().endswith(".pdf")
            or chat_file.content_type == "application/pdf"
        ):
            try:
                pdf_stream = io.BytesIO(file_bytes)
                reader = PdfReader(pdf_stream)

                text_pages = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_pages.append(text)

                extracted_text = "\n".join(text_pages)

                if not extracted_text.strip():
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Could not extract text from PDF. Ensure it is not an image-only scanned file."
                        },
                    )
            except Exception as e:
                return JSONResponse(
                    status_code=422,
                    content={
                        "error": f"Failed to parse PDF file structural layers: {str(e)}"
                    },
                )
        else:
            try:
                extracted_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                extracted_text = file_bytes.decode("latin-1")

    # Bundle data fields explicitly for network serialization forwarding
    data = {
        "user_message": user_message,
        "resume_text": extracted_text,
        "model_used": MODEL_NAME,
    }

    async with httpx.AsyncClient() as client:
        try:
            # Relay request over to the standalone Python backend instance
            response = await client.post(BACKEND_URL, data=data, timeout=None)

            # Forward backend's SkillGapResult response dictionary right back to your JS agent
            return JSONResponse(
                content=response.json(), status_code=response.status_code
            )

        except httpx.ConnectError:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Backend microservice unreachable. Verify port 8000 configuration status."
                },
            )
        except httpx.ReadTimeout:
            return JSONResponse(
                status_code=504,
                content={
                    "error": "The AI model took too long to respond. Please try again."
                },
            )
