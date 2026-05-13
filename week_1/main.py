# CLI Orchestrator (The Conductor)

from pathlib import Path
from src.ingestor import ingest_all_mhtml

SOURCE_DIR = Path("week_1/data/0_source")
BRONZE_DIR = Path("week_1/data/1_bronze")

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    print("\nweek1 python main.py ingest")
    print("🥉 Bronze:...") 
    ingest_all_mhtml(input_dir, output_dir)
    
def main():
    run_bronze()

if __name__ == "__main__":
    main()
