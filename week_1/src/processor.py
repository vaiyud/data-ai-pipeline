# Day 2: Cleans/Validates to data/2_silver/

from pathlib import Path
from bs4 import BeautifulSoup

def process_all_html(input_dir, output_dir):

    output_dir.mkdir(parents=True, exist_ok=True) # for program idempotency

    processed, skipped = 0, 0
    html_files = list(input_dir.glob("*.html"))

    if not html_files:
        print(f"No .html files found in {input_dir}")
        return
    
    for job_ad in html_files:
        try:
            # read from 1_bronze
            with open(job_ad, "r", encoding="utf-8", errors="ignore") as fp:
                
                # strip HTML tags
                soup = BeautifulSoup(fp, 'html.parser')
                # print(soup.prettify())
                print(soup.get_text(separator=" ", strip=True))
                
                # derive source_id from metadata
                # clean text
                # validate with Pydantic
                # save to 2_silver/*.json

        except Exception as e:
            print(f"❌ Error processing {job_ad.name}: {e}")
            skipped += 1
    
    print("\n📊 Silver Summary:")
    print(f"Total: {processed + skipped} | Processed: {processed} | Skipped: {skipped}")