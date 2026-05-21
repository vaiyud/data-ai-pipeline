import re
import time
import sqlite3
from pathlib import Path
from pydantic import BaseModel
from prompt_model import prompt_model

DB_PATH = Path("data/jobs_d1.db")
INPUT_FILE = Path("data/resume_d3.txt")

class SkillGapResult(BaseModel):
    gaps: list[str]

def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    
    max_retries = 3
    retry_duration = 2

    for attempt_num in range(1, max_retries + 1):
        try:
            with open(input_file_path, "r", encoding="utf-8", errors="ignore") as f:
                resume = f.read()

            resume_prompt = (
                f"Extract a comma-separated list of technical skills, languages, and tools from this resume. "
                f"Rules:\n"
                f"1. Output MUST be a single line of flat, comma-separated values.\n"
                f"2. Do NOT use bullet points, newlines, or markdown blocks.\n"
                f"3. If no technical skills are found, reply with 'None'.\n\n"
                f"Resume Content:\n{resume}"
            )

            response = prompt_model("gemma3:1b", resume_prompt)
            if not response:
                raise ValueError("Model returned an empty string.")

            # remove thinking process block if exists
            if "</thought>" in response:
                response = response.split("</thought>")[-1]

            # skills from resume
            # split response extracted from resume by comma, new line, tab, or spaces
            raw_skills = re.split(r"[,\n\r\t]+", response)
            resume_skills = set()
            for item in raw_skills:
                # remove dashes, asterisks, bullet points at the begining of the skill
                clean_skill = re.sub(r"^[\s\-\*\•]+", "", item).strip().lower()
                if clean_skill and clean_skill not in ["none/general/non-technical", "not applicable"]:
                    resume_skills.add(clean_skill)
            # print("Resume Skills: ", resume_skills)

            connection = sqlite3.connect(db_url)
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()

            cursor.execute(
                """
                    SELECT tech_stack
                    FROM jobs
                    WHERE tech_stack IS NOT NULL
                """
            )
            rows = cursor.fetchall()

            # skills from db
            db_skills = set()
            for row in rows:
                raw_db_skills = row["tech_stack"].split(",")
                for skill in raw_db_skills:
                    clean_db_skill = skill.strip().lower()
                    if clean_db_skill and clean_db_skill not in ["none/general/non-technical", "not applicable"]:
                        db_skills.add(clean_db_skill)
            # print("DB Skills: ", db_skills)
        
            gaps = []
            for skill in db_skills:
                if skill not in resume_skills:
                    gaps.append(skill)

            return SkillGapResult(gaps=sorted(gaps))

        except Exception as e:
            print(f"Attempt {attempt_num} failed: {str(e)}")

            if attempt_num < max_retries:
                time.sleep(retry_duration)
                print(f"Retrying in {retry_duration}s...")
            else:
                print("Max retries reached. Exiting...")
                return SkillGapResult(gaps=[])

if __name__ == "__main__":
     
    if not DB_PATH.exists():
        print(f"❌ Error: Database file not found at {DB_PATH}")
    elif not INPUT_FILE.exists():
        print(f"❌ Error: File file not found at {INPUT_FILE}")
    else:
        print("gaps=", find_skill_gaps(INPUT_FILE, DB_PATH).gaps)