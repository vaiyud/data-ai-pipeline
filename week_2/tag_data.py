import time
import sqlite3
from pathlib import Path
from prompt_model import prompt_model

DB_PATH = Path("data/jobs_d1.db")
# DB_PATH = Path("data/jobs.db")

def tag_data(db_url: str):

    batch_num = 0
    batch_size = 25
    max_retries = 3
    retry_duration = 5
	
    connection = sqlite3.connect(db_url)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    processed = False

    while True:
        cursor.execute(
            """
                SELECT source_id, description
                FROM jobs
                WHERE tech_stack IS NULL
                LIMIT ?
            """,
            (batch_size,)
        )
        rows = cursor.fetchall()

        if not rows:
            if batch_num == 0 and not processed:
                print("No data to tag")
            break
        
        processed = True
        print(f"\n[Batch {batch_num}] ({len(rows)} jobs)")

        for row in rows:
            source_id = row["source_id"]
            description = row["description"]

            ts_prompt = (
                f"Extract a comma-separated list of technical skills, languages, and tools from this text. "
                f"e.g. SQL, Python, Java, Spring Framework/Spring Boot, R\n"
                f"Rules:\n"
                f"1. Output MUST be a single line of flat, comma-separated values.\n"
                f"2. Do NOT use bullet points, newlines, or markdown blocks.\n"
                f"3. If no technical skills are found, reply with the single word 'None'.\n\n"
                f"Text to analyze:\n{description}"
            )

            extracted_tech_stack = ""
            attempt_num = 1
            success = False
            
            while attempt_num <= max_retries and not success:
                try:
                    response = prompt_model("gemma3:1b", ts_prompt)

                    # clean raw response into suitable tech_stack output format

                    # remove thinking process block if exists
                    if "</thought>" in response:
                        response = response.split("</thought>")[-1]
                        # print("Removed thinking process block:\n", response)
                    
                    # remove markdown and trim spaces
                    response = response.replace("```", "").strip(" \n\r\t,")
                    # print("Removed markdown and trim spaces:\n", response)
                    
                    # output response to a single line
                    response = response.replace("\n", ", ").replace("\r", ", ")
                    # print("Output response to a single line:\n", response)
                    
                    # remove bullet points and categories
                    for junk in ["- ", "* ", ":", "Technical Skills", "Tools", "Languages"]:
                        response = response.replace(junk, "")
                    # print("Removed bullet points and categories:\n", response)
                    
                    # remove duplicate commas and extra white spaces
                    items = [i.strip() for i in response.split(",") if i.strip()]
                    # print("Removed duplicate commas and extra white spaces:\n", items)
                    
                    extracted_tech_stack = ", ".join(items)
                    
                    if "none" in extracted_tech_stack.lower() or not extracted_tech_stack:
                        extracted_tech_stack = "None/General/Non-Technical"
                        success = True 
                        raise ValueError("Model returned None as no technical skills found.")
                    elif extracted_tech_stack:
                        success = True
                    else:
                        raise ValueError("Model returned an empty string.") 
                       
                except Exception as e:
                    print(f"[Batch {batch_num}] Attempt {attempt_num} failed: {str(e)}")
                    attempt_num += 1
                    if attempt_num <= max_retries:
                        time.sleep(retry_duration)
            if success:
                cursor.execute(
                    """
                        UPDATE jobs
                        SET tech_stack = ?
                        WHERE source_id = ?
                    """,
                    (extracted_tech_stack, source_id)
                )
                connection.commit()
                print(f"Analyzed Job {source_id}: {extracted_tech_stack}")
            else:
                print(f"[Batch {batch_num}] Job {source_id} skipped after max retries failed")
        
        batch_num += 1
                 	
    connection.close()

if __name__ == "__main__":
     
    if not DB_PATH.exists():
        print(f"❌ Error: Database file not found at {DB_PATH}")
    else:
        tag_data(DB_PATH)