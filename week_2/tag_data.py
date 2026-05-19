import time
import sqlite3
from pathlib import Path
from prompt_model import prompt_model

DB_PATH = Path("data/jobs_d1.db")

def tag_data(db_url: str):

    batch_num = 0
    batch_size = 10
    max_retries = 3
    retry_duration = 2
	
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
        print(f"\n[Batch {batch_num}] ({len(rows)} jobs left)")

        for row in rows:
             source_id = row["source_id"]
             description = row["description"]

             ts_prompt = (
                  f"Extract a comma-separated single-line list of technical skills, languages, and tools from this text. "
                  f"Response format example: SQL, Python, Java, Spring Framework/Spring Boot, R, Excel, Tableau, PowerBI, DataStudio, A/B testing, feature engineering, labeling"
                  f"If no technical skills are found, reply with the single word 'None'. Do not hallucinate response. "
                  f"Do not include explanations or categorization of skills, languages, and tools extracted.\n\n"
                  f"Text to analyze:\n{description}"
             )

             extracted_tech_stack = ""
             attempt_num = 1
             success = False

             while attempt_num <= max_retries and not success:
                  
                  try:
                       response = prompt_model("deepseek-r1:1.5b", ts_prompt)

                       if "</thought>" in response:
                           extracted_tech_stack = response.split("</thought>")[-1]
                       else:
                           extracted_tech_stack = response
                    
                       extracted_tech_stack = extracted_tech_stack.replace("```", "").strip(" \n\r\t,")

                       if "none" in extracted_tech_stack.lower() or not extracted_tech_stack:
                           raise ValueError("Model returned None as no technical skills found.")
                        #    extracted_tech_stack = "None/General/Non-Technical"
                        #    success = True 
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
                print(f"[Batch {batch_num}] Job {source_id} skipped after max retried failed")
        
        batch_num += 1
                 	
    connection.close()

if __name__ == "__main__":
     
     if not DB_PATH.exists():
        print(f"❌ Error: Database file not found at {DB_PATH}")
     else:
        tag_data(DB_PATH)