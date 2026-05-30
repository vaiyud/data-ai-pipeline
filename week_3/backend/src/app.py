import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from week_2.find_skill_gaps import find_skill_gaps, SkillGapResult

env_db_path = os.getenv("DB_PATH")
if not env_db_path:
    parent_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=parent_env_path)
    env_db_path = os.getenv("DB_PATH")

DB_PATH = Path(env_db_path)

app = FastAPI()


@app.post("/chat")
async def chat(user_message: str = Form(""), chat_file: UploadFile = File(...)):
    if not chat_file or not chat_file.filename:
        raise HTTPException(status_code=400, detail="File cannot be empty!")

    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / chat_file.filename

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(chat_file.file, buffer)

        result: SkillGapResult = find_skill_gaps(str(temp_file_path), DB_PATH)

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
