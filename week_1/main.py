from pathlib import Path
from src.ingestor import ingest_all_mhtml
import sys

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")

def run_bronze():
    input_dir = SOURCE_DIR
    output_dir = BRONZE_DIR
    print("🥉 Bronze:...") 
    ingest_all_mhtml(input_dir, output_dir)
    
def main():
    # CLI Orchestrator (The Conductor)
    command_list = ["ingest", "help"]

    if len(sys.argv) < 2:
        print("▶️ Usage: python main.py [command]")
        print(f"🛠️ Commands: {', '.join(command_list)}")
        return

    command = sys.argv[1].lower()

    match command:
        case "ingest":
            run_bronze()
        case "help":
            print(f"🛠️ Available commands: {', '.join(command_list)}")
        case _:
            print(f"❌ '{command}' : command does not exist!")
            print(f"🛠️ Supported commands: {', '.join(command_list)}. Try python main.py ingest.")

if __name__ == "__main__":
    main()
