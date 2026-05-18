# Day 4: Quality checks on Gold layer

import sqlite3
from pathlib import Path

def run_data_profile(db_path):

    # for program idempotency
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        # sql queries for quality check
        # total - returns total num of records
        cursor.execute("SELECT COUNT(*) FROM jobs")
        total = cursor.fetchone()[0]
        print(f"📈 Total Records: {total}")

        # missing values
        # returns total num of missing values in job_title column
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE job_title IS NULL")
        missing_job_title = cursor.fetchone()[0]
        # returns total num of missing values in company column
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE company IS NULL")
        missing_company = cursor.fetchone()[0]
        # returns total num of missing values in description column
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE description IS NULL")
        missing_desc = cursor.fetchone()[0]

        print(f"❓ Missing Values -> job_title: {missing_job_title}, company: {missing_company}, description: {missing_desc}")

        # returns average length of description in chars
        cursor.execute("SELECT AVG(LENGTH(description)) FROM jobs")
        avg_desc = cursor.fetchone()[0]
        print(f"📝 Avg Description Length: {int(avg_desc)} chars")

        # short_desc: return the shortest length of description in chars, and the source_id & job_title of that shortest description
        cursor.execute("""
                    SELECT source_id, job_title, LENGTH(description) as d 
                    FROM jobs
                    WHERE description IS NOT NULL 
                    ORDER BY d ASC
                    LIMIT 1
                    """)
        short_desc = cursor.fetchone()
        print(f"⚠️  Shortest Description: {short_desc['d']} chars")
        print(f" ↳ source_id: {short_desc['source_id']} | job_title: {short_desc['job_title']}")

        # long_desc: return the longest length of description in chars, and the source_id & job_title of that longest description
        cursor.execute("""
                    SELECT source_id, job_title, LENGTH(description) as d 
                    FROM jobs 
                    ORDER BY d DESC
                    LIMIT 1
                    """)
        long_desc = cursor.fetchone()
        print(f"🚨 Longest Description: {long_desc['d']} chars")
        print(f" ↳ source_id: {long_desc['source_id']} | job_title: {long_desc['job_title']}")

    except Exception as e:
        print(f"Profiling Error: {e}")
    finally:
        connection.close()
