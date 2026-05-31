import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse

from week_2.find_skill_gaps import find_skill_gaps, SkillGapResult
from week_2.prompt_model import prompt_model
from week_2.utils import get_file_summary

DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    parent_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=parent_env_path)
    DB_PATH = os.getenv("DB_PATH")

if not DB_PATH:
    raise RuntimeError("❌ 'DB_PATH' environment variable is missing.")

MODEL_NAME = os.getenv("DEFAULT_MODEL")
if not MODEL_NAME:
    parent_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=parent_env_path)
    MODEL_NAME = os.getenv("DEFAULT_MODEL")

if not MODEL_NAME:
    raise RuntimeError("❌ 'MODEL_NAME' environment variable is missing.")

app = FastAPI()


@app.post("/chat")
async def chat(
    user_message: str = Form(""),
    resume_text: str = Form(""),
    model_used: str = Form(""),
):
    message = user_message.strip()
    resume = resume_text.strip()

    if not message and not resume:
        raise HTTPException(
            status_code=400,
            detail="Your chat query message and file parameters cannot both be empty.",
        )

    if not resume:
        if message.lower() in ["hello", "hi", "hey", "start", "welcome", "help"]:
            welcome_reply = (
                "👋 Welcome to the Resume Helper Chatbot!\n\n"
                "I can help you evaluate your technical profile and find career paths. Here is how you can use me:\n"
                "1. Ask me any technical career questions directly here.\n"
                "2. Summarize a Resume: Upload your resume and get a concise summary of your resume.\n"
                "3. Identify Skill Gaps: Upload your resume and compare your experience against our job database targets."
            )
            return JSONResponse(
                content={
                    "chat_response": welcome_reply,
                    "model_used": model_used,
                    "type": "text",
                }
            )
        try:
            reply = prompt_model(model_used, message)
            return JSONResponse(
                content={
                    "chat_response": reply,
                    "model_used": model_used,
                    "type": "text",
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500, content={"error": f"Chat prompt failed: {str(e)}"}
            )

    user_intent = message.lower()
    if (
        "summary" in user_intent
        or "summarize" in user_intent
        or "summarise" in user_intent
    ):
        try:
            summary = get_file_summary(resume_text, user_message)
            return JSONResponse(
                content={
                    "chat_response": summary,
                    "model_used": model_used,
                    "type": "text",
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500, content={"error": f"Summary failed: {str(e)}"}
            )
    elif "skill gaps" in user_intent:
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_file_path = temp_dir / "extracted_resume.txt"

        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(resume_text)

            result: SkillGapResult = find_skill_gaps(
                str(temp_file_path), DB_PATH, model_name=model_used
            )

            return JSONResponse(
                content={"gaps": result.gaps, "model_used": model_used, "type": "gaps"}
            )

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Internal automation script processing failure: {str(e)}"
                },
            )
        finally:
            if temp_file_path.exists():
                os.remove(temp_file_path)
