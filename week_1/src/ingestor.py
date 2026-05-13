# Day 1: Extracts to data/1_bronze/

from pathlib import Path
import email
import quopri

def ingest_all_mhtml(input_dir, output_dir):
    
    output_dir.mkdir(parents=True, exist_ok=True) # for program idempotency

    extracted, failed = 0, 0
    mhtml_files = list(input_dir.glob("*.mhtml"))

    if not mhtml_files:
        print(f"No .mhtml files found in {input_dir}")
        return
    
    for job_ad in mhtml_files:
        try:
            # read from 0_source
            with open(job_ad, "r", encoding="utf-8", errors="ignore") as f:
                job = email.message_from_file(f)

            html_found = False

            for part in job.walk():
                if part.get_content_type() == "text/html":
                    html_content = part.get_payload() # payload = content
                    decoded_html = quopri.decodestring(html_content)
                    decoded_html_str = decoded_html.decode("utf-8", errors="replace")
                    output_job_ad = output_dir / f"{job_ad.stem}.html" # for program idempotency

                    # write to 1_bronze
                    with open(output_job_ad, "w", encoding="utf-8") as f_out:
                        f_out.write(decoded_html_str)
                    
                    print(f"✅ Extracted: {job_ad.name}")
                    extracted += 1
                    html_found = True
                    break

            if not html_found:
                print(f"⚠️ No HTML content found in: {job_ad.name}")
                failed += 1
        
        except Exception as e:
            print(f"❌ Error ingesting {job_ad.name}: {e}")
            failed += 1
    
    print("\n📊 Bronze Summary:")
    print(f"Total: {extracted + failed} | Extracted: {extracted} | Failed: {failed}")