# Day 1: Extracts to data/1_bronze/
import os
import email, email.message
from email.message import EmailMessage

def ingest_all_mhtml(input_dir, output_dir):
    files, dirs = 0, 0
    for root, dirnames, filenames in os.walk(input_dir):
        print('Looking in:', root)
        dirs += len(dirnames)
        files += len(filenames)
    print('Files:', files)
    print('Directories:', dirs)
    print('Total:', files + dirs)


PATH = r'week_1\data\0_source'

# files = 0
# for root, _, filenames in os.walk(PATH):
#     print('Looking in:', root)
#     files += len(filenames)
# print('Files:', files)
# print('Total:', files)

# msg = EmailMessage()
# msg['Subject'] = 'Test Email'
# msg['From'] = 'sender@example.com'
# msg['To'] = 'recipient@example.com'
# msg.set_content('This is a plain text email message.')

# print('msg.as_string():\n', msg.as_string())
# print('msg.get_content_type(): ', msg.get_content_type())

job_ad = r"week_1\data\0_source\AI Engineer – Machine Learning & Edge AI (Computer Vision) Job in Kelana Jaya, Selangor - Jobstreet.mhtml"

with open(job_ad, "r") as f:
    job = email.message_from_file(f)

extracted, failed = 0, 0
for part in job.walk():
    content_type = part.get_content_type() # gets all parts content type
    print('Filename: ', part.get_filename())
    if content_type == "text/html":
        html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
        extracted += len(part)
        print("HTML content found!")
        # print(html_content)
        # print(part.get_payload()) # payloads = content
        # print(part.get_content_charset())
    else:
        failed += len(part)
        print("HTML content NOT found!")

print('\njob.get_content_type(): ', job.get_content_type()) # gets the top most content type

with open('week_1\data\1_bronze\job_01.html', "w") as f:
    f.write(html_content)
    print("Extracted & saved HTML content!")

# --- output format ---
print("\nWeek 1: python main.py ingest")
print("🥉 Bronze: ...") 
# print(f"⚠️ No HTML content found in: {filename}")
# print(f"✅ Extracted: {filename}")
print("\n📊 Bronze Summary:")
print(f"Total: {extracted + failed} | Extracted: {extracted} | Failed: {failed}")