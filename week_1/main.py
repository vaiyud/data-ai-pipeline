import sys
from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
DB_NAME = "jobs.db"

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    print("\n🥉 Bronze:...")
    ingest_all_mhtml(input_dir, output_dir)

def run_silver():
    input_dir = BRONZE_DIR
    output_dir = SILVER_DIR
    print("\n🥈 Silver:...")
    process_all_html(input_dir, output_dir)

def run_gold():
    input_dir = SILVER_DIR
    output_dir = GOLD_DIR
    print("\n🥇 Gold:...")
    load_all_jsons(input_dir, output_dir)

def run_profiler():
    db_path = GOLD_DIR / DB_NAME
    print("\n--- 🔍 DATA QUALITY REPORT ---")
    run_data_profile(db_path)

def main():
    # CLI Orchestrator (The Conductor)
    command_list = ["ingest", "process", "load", "profile", "all"]

    if len(sys.argv) < 2:
        print(f"Usage: python main.py [{' | '.join(command_list)}]")
        return

    command = sys.argv[1].lower()

    match command:
        case "ingest":
            run_bronze()
        case "process":
            run_silver()
        case "load":
            run_gold()
        case "profile":
            run_profiler()
        case "all":
            run_bronze()
            run_silver()
            run_gold()
            run_profiler()
        case _:
            print(f"❌ '{command}' : command does not exist!")
            print(f"🛠️ Supported commands: {' | '.join(command_list)}. Try python main.py ingest.")

if __name__ == "__main__":
    main()
