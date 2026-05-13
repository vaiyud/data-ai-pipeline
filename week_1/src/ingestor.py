# Day 1: Extracts to data/1_bronze/

import os
from pathlib import Path
import email, email.message
from email.message import EmailMessage
import quopri

def ingest_all_mhtml(input_dir, output_dir):
    files, dirs = 0, 0
    for root, dirnames, filenames in os.walk(input_dir):
        print('Looking in:', root)
        dirs += len(dirnames)
        files += len(filenames)
    print('Files:', files)
    print('Directories:', dirs)
    print('Total:', files + dirs)


# PATH = r'week_1\data\0_source'

# files = 0
# for root, _, filenames in os.walk(PATH):
#     print('Looking in:', root)
#     files += len(filenames)
# print('Files:', files)
# print('Total:', files)

# print('msg.as_string():\n', msg.as_string())
# print('msg.get_content_type(): ', msg.get_content_type())

job_ad = r"week_1\data\0_source\AI Engineer – Machine Learning & Edge AI (Computer Vision) Job in Kelana Jaya, Selangor - Jobstreet.mhtml"

with open(job_ad, "r") as f:
    job = email.message_from_file(f)

extracted, failed = 0, 0
decoded_html = ''
for part in job.walk():
    content_type = part.get_content_type() # gets all parts content type
    print('Filename: ', part.get_filename())
    if content_type == "text/html":
        # html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
        html_content = part.get_payload()
        extracted += len(part)
        print("HTML content found!")
        # print('Keys():')
        # print(part.keys())
        # print('Values():')
        # print(part.values())
        # print('Items():')
        # print(part.items())
        print("Decoded HTML:")
        decoded_html = quopri.decodestring(html_content)
        print(decoded_html.decode('utf-8'))
        # print(html_content)
        # print(part.get_payload()) # payloads = content
        # print(part.get_content_charset())
    else:
        failed += len(part)
        print("HTML content NOT found!")

print('\njob.get_content_type(): ', job.get_content_type()) # gets the top most content type

from_dir = Path("week_1/data/0_source")
to_dir = Path("week_1/data/1_bronze/job_01.html")
# output_file.parent.mkdir(exist_ok=True, parents=True)
# Path.touch(mode=0o666, exist_ok=True)
# to_dir.write_text(decoded_html)
decoded_html_str = decoded_html.decode("utf-8").encode('cp850','replace').decode('cp850')
with open(to_dir, 'w') as f:
    f.write(decoded_html_str)
# to_dir.write_text('sample text')

# with open("week_1\data\1_bronze\job_01.html, "w") as f:
#     f.write(decoded_html)
#     print("Decoded & saved HTML content!")

# --- output format ---
print("\nWeek 1: python main.py ingest")
print("🥉 Bronze: ...") 
# print(f"⚠️ No HTML content found in: {filename}")
# print(f"✅ Extracted: {filename}")
print("\n📊 Bronze Summary:")
print(f"Total: {extracted + failed} | Extracted: {extracted} | Failed: {failed}")