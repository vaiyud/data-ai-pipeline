
# Week 1: Data Component


## Project Description
The project's goal is to build a local **data engineering pipeline** that successfully extracts raw data like unstructured job market data in **MHTML**, converts them into **HTML** and cleans it into a structured format in **JSON** using **Pydantic**, and stores it into a **SQLite database** (jobs.db) where job descriptions are sanitized into human-readable text. By the end of this project, the pipeline can be orchestrated with a fully functional **CLI tool** that was built with **idempotency** and **data quality checks** to ensure reliable and repeatable transiion from raw web archives to a structured knowledge base.

## Setup Instructions
Steps to initialize the local development environment and data pipeline:

### 1. Prerequisites

    - Python: 3.14.*
    - uv: 0.8.*
    - Git

### 2. Installation & Environment Setup

*On terminal*

**Clone the repository:**

    git clone https://github.com/vaiyud/data-ai-pipeline.git
    cd week_1

**Install and create virtual environment:**

    uv python install 3.14
    uv venv

**Activate virtual environment:**

    # Windows:
    .venv\Scripts\activate
    
    # macOS/Linux:
    source .venv/bin/activate

**Install dependencies:**

    uv sync

**Run the FULL pipeline:**

    python main.py all

### 3. Project Security

Make sure your `.gitignore` file includes the following:

    data/
    src/__pycache__/
    .ruff_cache/
    .venv/

## Usage
Run the orchestrator:

    python main.py [command]

### Supported Commands
| Command | Description |
|--|--|
| `ingest` | Extracts raw content from MHTML files into the directory in HTML format. |
| `process` | Sanitizes HTML, parses key fields into JSON, and validates schema before saving to the directory. |
| `load` | Performs idempotent inserts of JSON data into the SQLite `jobs.db`. |
| `profile` | Executes data quality checks and generates a summary report of the database. |
| `all` | Runs the entire end-to-end pipeline in the correct sequence. | 

### Sample Outputs

#### 1. Ingesting Data (ingest)

    🥉 Bronze:...
    ⚠️ No HTML content found in: <TITLE_0>.mhtml
    ✅ Extracted: <TITLE_1>.mhtml
    ✅ Extracted: <TITLE_2>.mhtml
    
    📊 Bronze Summary:
    Total: 3 | Extracted: 2 | Failed: 1

#### 2. Processing Data (process)

    🥈 Silver:...
    ⚠️ Missing job_title in: <TITLE_1>.html
    ⚠️ Missing description in: <TITLE_2>.html
    ⚠️ Missing company in: <TITLE_3>.html
    ✅ Processed: <TITLE_4>.html
    ✅ Processed: <TITLE_5>.html
    
    📊 Silver Summary:
    Total: 5 | Processed: 2 | Skipped: 3

#### 3. Loading Data (load)

    🥇 Gold:...
    ✅ Inserted: <TITLE_1>.json
    ✅ Inserted: <TITLE_2>.json
    ⏭️ Skipped (duplicate): <TITLE_3>.json
    ✅ Inserted: <TITLE_4>.json
    
    📊 Gold Summary:
    Total: 4 | Inserted: 3 | Skipped: 1

#### 4. Data Profiling (profile)

    --- 🔍 DATA QUALITY REPORT ---
    📈 Total Records: 84
    ❓ Missing Values -> job_title: 0, company: 0, description: 0
    📝 Avg Description Length: 2654 chars
    ⚠️ Shortest Description: 32 chars
    ↳ source_id: <SOURCE_ID> | job_title: <JOB_TITLE>
    🚨 Longest Description: 6781 chars
    ↳ source_id: <SOURCE_ID> | job_title: <JOB_TITLE>

*Note:*
> If running commands individually, ensure you follow the order: 
> `ingest -> process -> load -> profile`
> 
> You can also safely run `python main.py all` multiple times as the system will skip files and database records that have already been successfully processed.

## Technical Reflections
### Module 1: The Extractor (Medallion & Lakehouses)

Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?

**Answer**:

  

### Module 2: Treatment Plant (ETL vs ELT & Scale)

Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?

**Answer**:

  

### Module 3: The Blueprint & The Vault (Storage & Contracts)

What should happen if an important field like job_title disappears? Why fail early instead of silently inserting nulls into DB? How does `INSERT OR IGNORE` help prevent duplicate records?

**Answer**:

  

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?

**Answer**: