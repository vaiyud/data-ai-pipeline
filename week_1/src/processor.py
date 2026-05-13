# Day 2: Cleans/Validates to data/2_silver/

import json
from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError

class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

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
            with open(job_ad, "r", encoding="utf-8") as fp:
                
                # strip HTML tags and clean text
                soup = BeautifulSoup(fp, 'html.parser')

                # checks for files that suppossed to be skipped but was processed
                def get_clean_text(tag, sep=" "):
                    if tag:
                        val = tag.get_text(separator=sep, strip=True)
                        return val if val else None
                    return None
                
                # derive source_id, job_title, company, description from html metadata
                # source_id
                og_url_tag = soup.find("meta", property="og:url")
                if og_url_tag:
                    url_content = og_url_tag.get("content", "").strip()
                    if url_content:
                        source_id = url_content.split("/")[-1]

                if not source_id: print(f"⚠️ Missing source_id in: {job_ad.name}")
                
                # job_title
                job_title = get_clean_text(soup.find(attrs={"data-automation": "job-detail-title"}))
                if not job_title: print(f"⚠️ Missing job_title in: {job_ad.name}")

                # company
                company = get_clean_text(soup.find(attrs={"data-automation": "advertiser-name"}))
                if not company: print(f"⚠️ Missing company in: {job_ad.name}")

                # description
                description = get_clean_text(soup.find(attrs={"data-automation": "jobAdDetails"}), sep="\n")
                if not description: print(f"⚠️ Missing description in: {job_ad.name}")

                # validate with Pydantic
                job_data = JobListing(
                    source_id=source_id,
                    job_title=job_title,
                    company=company,
                    description=description
                )

                # write to 2_silver
                processed_job_ad = output_dir / f"{job_ad.stem}.json" # for program idempotency
                json_content = job_data.model_dump_json(indent=4)
                with open(processed_job_ad, "w", encoding="utf-8") as fj:
                    fj.write(json_content)
                
                print(f"✅ Processed: {job_ad.name}")
                processed += 1

        except (ValidationError, TypeError, ValueError):
            skipped += 1

        except Exception as e:
            print(f"❌ Error processing {job_ad.name}: {e}")
            skipped += 1
    
    print("\n📊 Silver Summary:")
    print(f"Total: {processed + skipped} | Processed: {processed} | Skipped: {skipped}")