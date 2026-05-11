# CLI Orchestrator (The Conductor)

from pathlib import Path # Figure out why use Path?
from src.ingestor import ingest_all_mhtml

SOURCE_DIR = Path("week_1/data/0_source")
BRONZE_DIR = Path("week_1/data/1_bronze")

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    ingest_all_mhtml(input_dir, output_dir)
    
def main():
    print("\nHello from Job ETL Orchestrator!")
    # ORCHESTRATION TO BE IMPLEMENTED HERE

if __name__ == "__main__":
    main()
