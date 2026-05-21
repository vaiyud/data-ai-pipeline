
# Week 2: AI Component


## Project Description
The project's goal is to build a **skill gap detection pipeline** using **large language models** (LLM) instead of rule-based system. The project will populate the `tech_stack` for each job in `jobs.db` created from week 1 using **LLM**, and then identify the skill gaps in deterministic manner by comparing the **skills extracted from the resume** using **LLM** and the skills populated and stored in `tech_stack` from `jobs.db`.

## Setup Instructions
Steps to initialize the local development environment and data pipeline:

### 1. Prerequisites

- Python: 3.14.*
- uv: 0.8.*
- ollama 0.21.*
- [Google AI API Key](https://aistudio.google.com/)

### 2. Installation & Environment Setup

*On terminal*

**Clone the repository:**

    git clone https://github.com/vaiyud/data-ai-pipeline.git
    cd week_2

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

### 3. Project Security

Make sure your `.gitignore` file includes the following:

    data/
    __pycache__/
    .ruff_cache/
    .venv/
    .env
Make sure your `.env` file includes the following:

    GOOGLE_API_KEY=<YOUR-API-KEY-HERE>

> Warning: DO NOT commit your `.env` containing any `API_KEY` to the repository.

## Usage
### Test `prompt_model.py`:

    uv run prompt_model.py <model_name> <prompt>

*Make sure your prompt is inside " ".*

#### Suggested Models

    gemma3:1b
    llama3.1
    phi3
    deepseek-r1:1.5b

You can also use your preferred model for this project. The below command will pull and run your preferred model from [ollama](https://ollama.com/library).

    ollama run <your-preferred-model>
To see all installed models available on your device:

    ollama list

#### Sample Output

    $ uv run prompt_model.py
    ❌ Error: Missing arguments
    🛠️ Usage: uv run prompt_model.py [gemma3:1b | deepseek-r1:1.5b | phi3 | llama3.1] <prompt>

    $ uv run prompt_model.py gemma3:1b "how many the r's are there in the word strawberry?"
    
    --- RESPONSE ---
    
    There are 3 “r”s in the word strawberry. 😊
    $ uv run prompt_model.py gemma3:27b "how many the r's are there in the word strawberry?"

    --- RESPONSE ---
    
    ❌ Error:  model 'gemma3:27b' not found (status code: 404)

### Execute `tag_data.py`:

To tag the data from the database:

    uv run tag_data.py

#### Sample Output

    $ uv run tag_data.py
    
    [Batch 0] (10 jobs)
    Analyzed Job 91237386: AI, Workflow Automation, APIs, Azure, OpenAI, Python, JavaScript, CRM, ERP, Automation
    [Batch 0] Attempt 1 failed: Model returned None as no technical skills found.
    Analyzed Job 91230331: Python, API Integration, AI Agents, SOAR, SIEM, Automation Frameworks, RESTful APIs, Security Scanning
    
### Execute `find_skill_gaps.py`:

To read the resume and the database to identify skill gaps:

    uv run find_skill_gaps.py

#### Sample Output

    $ uv run find_skill_gaps.py
    gaps=['a/b testing', 'alibaba cloud', 'api integration', 'aws', 'ci/cd', 'cloud', 'code reviews', 'data processing', 'datastudio', 'excel', 'feature engineering', 'github actions', 'google cloud', 'grafana', 'labeling', 'linux development environments', 'llm', 'mongodb', 'mysql', 'nginx', 'node.js', 'php', 'power bi', 'powerbi', 'prometheus', 'rag', 'restful api design', 'spring boot', 'spring framework', 'testing', 'web automation']

## API/Function Reference

### `prompt_model(model, prompt)`
**Purpose:** Handles execution logic for LLM inference by routing raw text strings to a locally hosted model endpoint and returning the response.

**Inputs:** 
- `model` (*str*): identifier tag of the targeted model (e.g. `gemma3:1b`)
- `prompt` (*str*): text instructions and context payload from user or other modules (e.g. `tag_data`, `find_skill_gaps`)

**Outputs:** Returns a *str* representing the raw textual output from the LLM.

### `tag_data(db_url)`

**Purpose:** Reads raw job descriptions from the target database, pipes them through the AI layer to isolate key technical competencies, and streams those normalized tools back into the database using a memory-safe batch pipeline.

**Inputs:** `db_url` (*str*): The local filesystem path directing to the SQLite database file.

**Outputs:** 
-   **Database:** Populates and saves the comma-separated technical keywords directly into the `tech_stack` column of the `jobs` table.
    
-   **Terminal:** Emits real-time batch numbers, job-by-job analysis indicators, and granular failure tracking logs directly to standard output.

**Modules Interactions:** Acts as a consumer of `prompt_model`, passing raw job descriptions to the inference engine to receive clean, extractable token options.

### `find_skill_gaps(input_file_path, db_url)`

**Purpose:** Extracts explicit candidate expertise from a raw text resume using generative AI, aggregates required market tech stacks from the database in flat blocks, and isolates missing requirements using RegEx sanitation and set-difference matching.

**Inputs:**

- `input_file_path` (*str*): path to unstructured plain-text resume file.
- `db_url` (*str*): path targeting the validated SQLite job database.

**Outputs:** 
- Returns a structured Pydantic `SkillGapResult` object encapsulating an array of missing skill strings.
- Emits a sorted visualization of that data directly to the terminal interface.

**Module Interactions:** Calls `prompt_model` exactly once up-front to construct the candidate's base skill profile.

## Data/Assumptions

### Data Architecture

The pipeline relies entirely on local file resources to ensure zero cloud data egress and low execution overhead.

**Input File (`resume.txt`):** A plain-text (`.txt`) file containing unstructured, raw text extracted from a candidate's resume.
    
**Database (`jobs.db`):** A local SQLite database file containing market job data created from the data engineering pipeline in week 1.
    
**Database Schema: `jobs` Table**
    
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| **source_id*** | TEXT | Unique identifier for each job posting. |
| **job_title** | TEXT | The professional title of the designated role. |
| **company** | TEXT | The name of the hiring organization. |
| **description** | TEXT | The primary source text containing raw market requirements. |
| **tech_stack** | TEXT | A nullable target column updated by `tag_data` with flat, comma-separated keywords (e.g., `python, docker, git`). |

**Primary Key*

### Input Format Expectations

-   The resume text file must use standard `utf-8` encoding.
    
-   The model responses are assumed to include standard reasoning syntax structures (wrapped in `<thought>...</thought>` blocks) which are sliced away automatically during the clean-up phase.

### Data Constraints & Sanitization

-   Non-technical placeholder labels injected by models (such as `"none"`, `"general"`, or `"non-technical"`) are explicitly treated as junk data and filtered out.
    
-   All string comparisons are strictly normalized to **lowercase** to ensure deterministic matching regardless of how text capitalization varies between job descriptions and resumes.

### Hardware Simplifications

To accommodate low-resource hardware constraints (e.g. 8GB RAM, Dual-Core systems), database parsing is hard-capped at a `batch_size = 25`**.

***which can be modified accordingly to the device's hardware that runs this code*


### Core Data Flow Diagram

The project's execution loop operates through a coordinated two-stage lifecycle—local job market profile aggregation followed by deterministic candidate skill gap evaluation.

[![](https://mermaid.ink/img/pako:eNp1VWFv2joU_StXqfbUSQElISmQSU-iQGnR-lo13ZfBhEzshIxgR7azwkr_-7txgALdAlJi595z7HNOklcrFpRZoZVKUizgeTDlgMenTzDKxZzkMCByCfdYA5He5BlPoS94kqWlJDoTvC6Pc6LUgCWgNEkZJFmehxcuq3620lIsWXjh-_7uuvGSUb0IvWK9n6BELYiUZBNCAIEdi1zI8CJJki9n-IUUMVNqx-BQL2h1DgyO1-lQ95TERZIdHHMSL2HniJRosoPzqEsc5wCXBO34MPwIlyTMmXvncCtUKt_j-a7vxQe89txNiPd3vBYLkgDxDg40Gg2InnujIbjVdT2vynltVfTswiQyershjMUc7tEqptEx3FEvTSVLjUU_6sbq6E2qukehNBqpfiDqv3A9ufwp5qpJ55-PKq-re9snRqgCylQss6LCUlvoXyLnrJKtWWw-v3f0TUfEOHYgIMSCa7bWWxhM0LVVoWdGmyOOwY5Dl5IrKIhUjIJm8QKWbPMiJK3Yzgm-FUjNlKmbYdziJTLl5Ypv4bquxRUcmWJ0MrH8spvo71O0n-jZ1yYG-_GgdvHPVnh_tMLbW-GF8MRUuWIw_EXy0hgA_8CIFNDjJN-oTB0pMJxIU9zUa127cXOZZJzO1BITNEtJoU5FvjkSuVIX6v4tjP4m8uhEZEleICacZpWIYFhQ5JtzgieWDtcQEZ7p7DeaEjH08fYVT41BhsGXjMcM86bjBQbp7b391mxiPIkqZNx0pUWu4XFDCddZDOPo4T94mP9ksT5a49iQPsqMawWVbOhvgtsBYSq3cDeJhNTVQircSk0Fz0yuMpQUHkpdlHu4D-Z7p-bf2Lfn9g_tO3t8EoDRxwDgS4_jUoRU9VT9fHwVhO4yu8uiMkpZNr5PM2qFWpbMtla4VFINrdeqe2rpBVuxqRXiJcWHdmpN-Rv2FIR_F2K1b5OiTBdWmJBc4ag0wR9kBDP3XoL7ZbIvSq6t0PM7BsMKX621Fbavmk6nc-UFfsvveh0Pb26s0G033at24HR8v9V18B-82dZvw-o23SDodlsdt-u1sCbwbYvRDDd9X38jzKfi7X95p_bi?type=png)](https://mermaid.live/edit#pako:eNp1VWFv2joU_StXqfbUSQElISmQSU-iQGnR-lo13ZfBhEzshIxgR7azwkr_-7txgALdAlJi595z7HNOklcrFpRZoZVKUizgeTDlgMenTzDKxZzkMCByCfdYA5He5BlPoS94kqWlJDoTvC6Pc6LUgCWgNEkZJFmehxcuq3620lIsWXjh-_7uuvGSUb0IvWK9n6BELYiUZBNCAIEdi1zI8CJJki9n-IUUMVNqx-BQL2h1DgyO1-lQ95TERZIdHHMSL2HniJRosoPzqEsc5wCXBO34MPwIlyTMmXvncCtUKt_j-a7vxQe89txNiPd3vBYLkgDxDg40Gg2InnujIbjVdT2vynltVfTswiQyershjMUc7tEqptEx3FEvTSVLjUU_6sbq6E2qukehNBqpfiDqv3A9ufwp5qpJ55-PKq-re9snRqgCylQss6LCUlvoXyLnrJKtWWw-v3f0TUfEOHYgIMSCa7bWWxhM0LVVoWdGmyOOwY5Dl5IrKIhUjIJm8QKWbPMiJK3Yzgm-FUjNlKmbYdziJTLl5Ypv4bquxRUcmWJ0MrH8spvo71O0n-jZ1yYG-_GgdvHPVnh_tMLbW-GF8MRUuWIw_EXy0hgA_8CIFNDjJN-oTB0pMJxIU9zUa127cXOZZJzO1BITNEtJoU5FvjkSuVIX6v4tjP4m8uhEZEleICacZpWIYFhQ5JtzgieWDtcQEZ7p7DeaEjH08fYVT41BhsGXjMcM86bjBQbp7b391mxiPIkqZNx0pUWu4XFDCddZDOPo4T94mP9ksT5a49iQPsqMawWVbOhvgtsBYSq3cDeJhNTVQircSk0Fz0yuMpQUHkpdlHu4D-Z7p-bf2Lfn9g_tO3t8EoDRxwDgS4_jUoRU9VT9fHwVhO4yu8uiMkpZNr5PM2qFWpbMtla4VFINrdeqe2rpBVuxqRXiJcWHdmpN-Rv2FIR_F2K1b5OiTBdWmJBc4ag0wR9kBDP3XoL7ZbIvSq6t0PM7BsMKX621Fbavmk6nc-UFfsvveh0Pb26s0G033at24HR8v9V18B-82dZvw-o23SDodlsdt-u1sCbwbYvRDDd9X38jzKfi7X95p_bi)

## Testing



## Limitations

### Model Dependability & Accuracy Trade-offs
**Model Selection Scale:** The extraction logic was verified exclusively using small-footprint local models (`deepseek-r1:1.5b` and `gemma3:1b`). While highly efficient on constrained consumer hardware, smaller parameter sizes carry a natural trade-off in linguistic reasoning compared to larger cloud models.

**Fuzzy Token Mismatches:** The matching engine relies on exact keyword parity. If the model extracts a skill as `"react"` but the database lists it as `"react.js"`, the deterministic set-difference logic treats them as completely separate entities, leading to false-positive skill gaps.

### Missing Features & Constraints
**No Experience or Seniority Grading:** The system processes technical skills as binary presence flags. It does not differentiate between junior-level exposure and senior-level experience of the skills, nor does it evaluate the depth of a candidate's professional certifications or non-technical skills.

**Static Local Dataset:** The system evaluates candidates against a static local SQLite database (`jobs.db`) built during the Week 1 data engineering pipeline. It lacks live web-scraping components or dynamic external API integrations to ingest real-time market shifts automatically.

## Architecture Reflections

### Design Choices
The core architectural choice was splitting the pipeline into two distinct scripts: `tag_data.py` (Stage 1) and `find_skill_gaps.py` (Stage 2). 

This separated the probabilistic AI extraction phase from the deterministic evaluation logic. Instead of asking the LLM to both extract and compare the data, which introduces hallucination risks and wastes context window tokens, the LLM is restricted strictly to unstructured-to-structured keyword extraction. The final gap analysis is handed off to local Python set operations and RegEx, which ensures 100% mathematical reliability and zero AI hallucination at the evaluation layer.

### Trade-offs

Operating under strict hardware limitations, **simplicity and low resource consumption** were prioritized over raw execution speed.

**In-Memory footprint vs. Network Latency:** Choosing local execution (`gemma3:1b` / `deepseek-r1:1.5b`) completely eliminated external API network dependencies and API cost scaling, but it shifted processing bottlenecks directly to local CPU/RAM performance.

**Transactional Batch Updates vs. Monolithic Writing:** Instead of opening expensive single-row database connections for every individual entry, the pipeline executes model inference and commits updates to `jobs.db` in optimized batches. This batching strategy significantly reduces database I/O overhead and avoids file locks. Crucially, structuring the workflow this way allows for prompt-batching optimizations, which directly minimizes API token usage and stays safely within the restrictive daily rate limits imposed by free-tier or local AI model endpoints.

### Future Improvements & Extensions
If given more time and scalable development resources, the architecture would be extended across four aspects:

**Cloud Integration & Model-Agnostic Flexibility:** The core prompt engine can modified into a generalized provider interface. This would allow the code to easily swap between local hardware backends and robust cloud-based environments, such as Google AI models (Gemini API), making the entire system fully open and adaptable to any commercial or open-source LLM provider.

**Model Context Protocol (MCP) Data Layer:** The direct, raw SQL execution strings inside the application scripts can be moved away in favor of leveraging MCP to call SQL scripts and manage database transactions indirectly. This decouples the core logic from SQLite-specific syntax and improves system security.

**Semantic Skill Graph Integration:** The strict string-matching set difference can be replaced with a semantic lookup table or vector embedding comparison (e.g., mapping `"React"` and `"React.js"` or `"FastAPI"` and `"Python Backend"` to the same node) to completely eliminate false-positive skill gaps.

**Dynamic API Layer:** The static Week 1 `jobs.db` dataset can be transitioned into an automated, live web-scraping queue to keep local job market trends continuously updated in real-time.
