# Day 3: Loads to data/3_gold/

import json
import sqlite3
from pathlib import Path

def load_all_jsons(input_dir, output_dir):

	# for program idempotency
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    db_file = output_path / "jobs.db"

    # create SQLite schema
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS jobs (
                source_id TEXT PRIMARY KEY, 
                job_title TEXT, 
                company TEXT,  
                description TEXT,
                tech_stack TEXT
            )
        """
    )
    connection.commit()

    inserted, skipped = 0, 0
    json_files = list(input_dir.glob("*.json"))

    if not json_files:
        print(f"No .json files found in {input_dir}")
        connection.close()
        return

    for job_ad in json_files:
        try:
            # read from 2_silver
            with open(job_ad, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            # load Silver JSON data into jobs.db
            # enforce identity using source_id
            # ensure idempotent inserts
            cursor.execute(
                """
                    INSERT OR IGNORE INTO jobs (
                            source_id, 
                            job_title, 
                            company, 
                            description,
                            tech_stack
                    )
                     VALUES (?, ?, ?, ?, ?)
                """,
                (
                    data["source_id"],
                    data["job_title"],
                    data["company"],
                    data["description"],
                    None,
                ),
            )

            # Check if a row was actually affected (not ignored as a duplicate)
            if cursor.rowcount > 0:
                print(f"✅ Inserted: {job_ad.name}")
                inserted += 1
            else:
                print(f"⏭️ Skipped (duplicate): {job_ad.name}")
                skipped += 1

        except Exception as e:
            print(f"❌ Error loading {job_ad.name}: {e}")
            skipped += 1

    connection.commit()
    connection.close()

    print("\n📊 Gold Summary:")
    print(f"Total: {inserted + skipped} | Inserted: {inserted} | Skipped: {skipped}")
