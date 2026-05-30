import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse

from week_2.find_skill_gaps import find_skill_gaps, SkillGapResult

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
async def chat(user_message: str = Form(""), resume_text: str = Form("")):

    if not resume_text or not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume content text cannot  empty! Please ensure the frontend is extracting text properly.",
        )

    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / "extracted_resume.txt"

    try:
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(resume_text)

        result: SkillGapResult = find_skill_gaps(
            str(temp_file_path), DB_PATH, MODEL_NAME
        )

        return JSONResponse(content={"gaps": result.gaps})

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
