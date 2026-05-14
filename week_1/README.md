
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

*Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?*

- **Answer:** Storing files in their raw format, like `.mhtml` or `.html`, enables us to reprocess the data in case something goes wrong when processing the data from the database in the later phases. It prevents data from disappearing completely from the database by replaying the pipeline. This repopulates it since the source files was kept in the data lake. Especially when the source data are archived web pages, it would not be possible to retrieve them again, as they will no longer be available online. Not only that, storing these raw files can be useful in the future, to expand the database, for instance, when others want to extract more information that was not initially extracted from the source files.


### Module 2: Treatment Plant (ETL vs ELT & Scale)

*Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?*

- **Answer:** Cloud systems prefer ELT to ETL because the cost of computing is higher than the cost of storage nowadays. It is more sustainable to process files via ELT as we can leverage the power of cloud data warehouses to perform the cleaning. Also, when files are processed sequentially, it can be time-consuming as the files required to be processed can grow over time. Unlike in this project, where sequential processing does not show a significant delay in processing 100 HTML files, a larger number of files will be required to be processed for a business report in industrial practices, and there will be a significant bottleneck. Distributed and parallel processing help reduce the time taken significantly, as we can utilize multiple cores or nodes to perform the tasks in parallel.
  

### Module 3: The Blueprint & The Vault (Storage & Contracts)

*What should happen if an important field like job_title disappears? Why fail early instead of silently inserting nulls into DB? How does `INSERT OR IGNORE` help prevent duplicate records?*

- **Answer:** Inserting null values to important fields like the `job_title` does not exactly break dashboards, for instance, but it will lead to incorrect data shown on the dashboard, making it misleading or messy for decision makers. Also, detecting an early fail allows teams to fix the error at the root level before it enters the database, which will be difficult to find and fix, especially on a larger scale. In this project, `INSERT OR IGNORE` was used to prevent duplicate records, so that, when the same process is run several times, the result will remain the same, as SQLite check the incoming `source_id` (the primary key) if it already exists in the table, drops that `INSERT` process, and moves on to the next row `INSERT` process.  

### Module 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

*What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?*

- **Answer:** When `processor.py` crashes halfway through a larger number of files via `main.py`, some files will be partially written, which might affect the next processes in the pipeline. Therefore, we have to manually figure out where to restart the pipeline. After fixing the issue, we will have to rerun the pipeline from the start. But with automated orchestration tools, it will not be necessary to do so as it will only retry from the interrupted layer in the pipeline. This can be set up using automated tools, which allows solving temporary issues like the database being busy or a network issue without manual intervention at any time of the day. Also, some automated orchestration tools have a searchable UI and send alerts to the teams to help keep track of any issues that occur during the run of the pipeline.