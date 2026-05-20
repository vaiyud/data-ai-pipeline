import time
import sqlite3
from pathlib import Path
from pydantic import BaseModel

DB_PATH = Path("data/jobs_d1.db")
INPUT_FILE = Path("data/resume_d3.txt")

class SkillGapResult(BaseModel):
    gaps: list[str]
    # add more fields when needed...

def find_skill_gaps(input_file_path: str, db_url: str) -> SkillGapResult:
    
    max_retries = 3
    retry_duration = 2

    for attempt_num in range(1, max_retries + 1):
        try:
            with open(input_file_path, "r", encoding="utf-8", errors="ignore") as f:
                resume = f.read().lower()

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

            # print(f"gaps={}")
            # return SkillGapResult(gaps=)

        except Exception as e:
            print(f"❌ Error: {e}")
            print(f"Attempt {attempt_num} failed: {str(e)}")

            if attempt_num <= max_retries:
                time.sleep(retry_duration)
                print(f"Retring in {retry_duration}s...")
            else:
                return SkillGapResult(gaps=[])

if __name__ == "__main__":
     
    if not DB_PATH.exists():
        print(f"❌ Error: Database file not found at {DB_PATH}")
    elif not INPUT_FILE.exists():
        print(f"❌ Error: File file not found at {INPUT_FILE}")
    else:
        find_skill_gaps(INPUT_FILE, DB_PATH)