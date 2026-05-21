
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

**Purpose:** Extracts explicit candidate expertise from a raw text resume using generative AI, aggregates required market tech stacks from the database, normalizes both sources using an alias mapping translation layer, and isolates missing requirements using RegEx sanitation and set-difference matching.

**Inputs:**

- `input_file_path` (*str*): path to unstructured plain-text resume file.
- `db_url` (*str*): path targeting the validated SQLite job database.

**Outputs:** 
- Returns a structured Pydantic `SkillGapResult` object encapsulating an array of missing skill strings.
- Emits a sorted visualization of that data directly to the terminal interface.

**Module Interactions:** 

- Calls `prompt_model` exactly once up-front to construct the candidate's base skill profile.

- Intercepts parsed tokens using an internal `ALIAS_MAP` dictionary function to normalize shorthand variances (such as handling `"C/C++"` expansions and protecting `"CI/CD"` strings) before comparison.

### `normalize_skills(raw_skills_set)`

**Purpose:** Acts as the engine's translation gatekeeper. It takes a raw set of extracted skills and maps individual shorthand names, synonyms, or compound tags into standardized tokens before comparison operations take place.

**Inputs:**
- `raw_skills_set` (*set*): A collection of raw, lowercased skill strings isolated from either the resume extraction or the database query.

**Outputs:**
- Returns a standardized, flattened `set` of normalized skill strings. 

**Module Interactions:** 
- Iterates through the input collection against the internal `ALIAS_MAP` dictionary. 
- Expands compound entries (e.g. single `c/c++` input into individual `c` and `c++` tokens) and converts known synonyms to their uniform equivalents, while allowing unmapped skills to pass through unchanged.

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

-   Extracted keywords are passed through an explicit **translation dictionary**, `ALIAS_MAP` to resolve compound conventions and structural variations. This process expands shorthand sets (e.g. decomposing `c/c++` into distinct `c` and `c++` tokens) while safeguarding unified terminology (e.g. protecting `ci/cd` or `a/b testing` from punctuation-based splits), ensuring data sets match perfectly during comparison.

### Hardware Simplifications

To accommodate low-resource hardware constraints (e.g. 8GB RAM, dual-core systems), database parsing is hard-capped at a `batch_size = 25`**.

***which can be modified accordingly to the device's hardware that runs this code*


### Core Data Flow Diagram

The project's execution loop operates through a coordinated two-stage lifecycle—local job market profile aggregation followed by deterministic candidate skill gap evaluation.

[![](https://mermaid.ink/img/pako:eNp1VWFv2joU_StXqfbU6QWUhKTQTHoSBUqL1rVqui-DCZnYCVkTO7KdFVb639-NAwzoFj5g39x7jn3OtfNqxYIyK7RSScolPA1nHPD58AHGuViQHIZEPsMd5kCk13nGUxgInmRpJYnOBG_S45woNWQJKE1SBkmW5-GZy-qfrbQUzyw8831_O269ZFQvQ69c7QKUqCWRkqxDCCCwY5ELGZ4lSfLpBL-UImZKbRkc6gWd3p7B8Xo96h6TuEiyhWNO4iXsFJESTbZwHnWJ4-zhkqAb76fv4ZKEOQvvFK5ApfIdnu_6XrzH6y7chHh_x-uwIAkQb-9Aq9WC6Kk_HoFbj5u4qhaNVdGTC9PI6O2GMBELuEOrmEbHcEf9NJUsNRZ9bwrrpz-t8x6E0mik-o6o_8HV9PyHWKg2XXw8yLyq320eGaEKKFOxzMoaS21gcI6c81q2drn--LtiYCoixrECASEWXLOV3sBwiq4VpZ4bbQ44hlsOXUmuoCRSMQqaxUt4ZusXIWnNdkrwtURqpkzeHNstfkamvCr4Bq6aXFzBgSlGJ9OWn7aBwa6LdoG-fWXaYDcfNi7-2Qrvj1Z4Oyu8EB6ZqgoGo58kr4wB8A-MSQl9TvK1ytSBAqOpNMltvdKNG9fnScbpXD1jB81TUqpjka8PRK7VhaZ-A-O_iTw-ElmSF4gJp1ktIhgWFPn6lOCRpaMVRIRnOvuFpkQMfbzrP5xzIQuSY6xZoYJ_of_5th_N8eXBMnFmcL7s0hGizq-BkO_mFf9bwwyPkGQ8Zti5Ol5iS779hrgxckympg7lq1XNNTysKeE6i2ES3X-B-8UPFuuD3U4M7YPMuFZQG4CdkqAwIEzmBm6nkZB6vx4EVvDEZJGhOXBf6bLawb1rI--4ja5t3KV9c9pMI_vWnhy10_h9O-EVynE5Qqom1Jy2z4LQ7QnYdrba6m7ZeD9n1Aq1rJhtFbhgUk-t17p-ZuklK9jMCnFI8RKYWTP-hjUl4d-EKHZlUlTp0goTkiucVeYgDTOCPVzso-gHZXIgKq6tMAh8A2KFr9bKClte56IdXHa7eOv6F-5l1_dsa43xwG33uh3fu3Ad1_OcnvtmW78Msdvudnrd4KLjXLod3-n4HdtiNMOd3zWfHfP1efsf5tUQfw?type=png)](https://mermaid.live/edit#pako:eNp1VWFv2joU_StXqfbU6QWUhKTQTHoSBUqL1rVqui-DCZnYCVkTO7KdFVb639-NAwzoFj5g39x7jn3OtfNqxYIyK7RSScolPA1nHPD58AHGuViQHIZEPsMd5kCk13nGUxgInmRpJYnOBG_S45woNWQJKE1SBkmW5-GZy-qfrbQUzyw8831_O269ZFQvQ69c7QKUqCWRkqxDCCCwY5ELGZ4lSfLpBL-UImZKbRkc6gWd3p7B8Xo96h6TuEiyhWNO4iXsFJESTbZwHnWJ4-zhkqAb76fv4ZKEOQvvFK5ApfIdnu_6XrzH6y7chHh_x-uwIAkQb-9Aq9WC6Kk_HoFbj5u4qhaNVdGTC9PI6O2GMBELuEOrmEbHcEf9NJUsNRZ9bwrrpz-t8x6E0mik-o6o_8HV9PyHWKg2XXw8yLyq320eGaEKKFOxzMoaS21gcI6c81q2drn--LtiYCoixrECASEWXLOV3sBwiq4VpZ4bbQ44hlsOXUmuoCRSMQqaxUt4ZusXIWnNdkrwtURqpkzeHNstfkamvCr4Bq6aXFzBgSlGJ9OWn7aBwa6LdoG-fWXaYDcfNi7-2Qrvj1Z4Oyu8EB6ZqgoGo58kr4wB8A-MSQl9TvK1ytSBAqOpNMltvdKNG9fnScbpXD1jB81TUqpjka8PRK7VhaZ-A-O_iTw-ElmSF4gJp1ktIhgWFPn6lOCRpaMVRIRnOvuFpkQMfbzrP5xzIQuSY6xZoYJ_of_5th_N8eXBMnFmcL7s0hGizq-BkO_mFf9bwwyPkGQ8Zti5Ol5iS779hrgxckympg7lq1XNNTysKeE6i2ES3X-B-8UPFuuD3U4M7YPMuFZQG4CdkqAwIEzmBm6nkZB6vx4EVvDEZJGhOXBf6bLawb1rI--4ja5t3KV9c9pMI_vWnhy10_h9O-EVynE5Qqom1Jy2z4LQ7QnYdrba6m7ZeD9n1Aq1rJhtFbhgUk-t17p-ZuklK9jMCnFI8RKYWTP-hjUl4d-EKHZlUlTp0goTkiucVeYgDTOCPVzso-gHZXIgKq6tMAh8A2KFr9bKClte56IdXHa7eOv6F-5l1_dsa43xwG33uh3fu3Ad1_OcnvtmW78Msdvudnrd4KLjXLod3-n4HdtiNMOd3zWfHfP1efsf5tUQfw)

## Testing

The system architecture was evaluated using a multi-tiered validation approach designed to test data aggregation stability, LLM parsing accuracy, and the strict determinism of the gap analysis logic.

### Test Scenarios

To ensure correctness, the matching engine was tested against three explicit edge-case scenarios. The table below outlines the core input conditions, how the raw pipeline failed initially, and how deterministic logic resolved the issue:

| Test Scenario | Target Input Conditions | Before Validation | After Validation |
| :--- | :--- | :--- | :--- |
| <br>Exact Keyword Match | A resume containing structured technical text that matches database fields exactly (e.g., `Python`, `Docker`, `Java`). | Basic tokenization succeeded, but arbitrary model capitalization variances occasionally caused false gap detection. | Strict string lowercasing guarantees exact matching tokens independent of formatting choices. |
| <br>Complex Phrase & Boundary Handling | A resume listing compound shorthand strings and unified variant formats (e.g., `C/C++`, `MYSQL`, `A/B Testing`). | The small local model completely missed `A/B Testing` embedded in body text. Hardcoded character splitting destroyed `CI/CD` while leaving `C/C++` unresolvable against database requirements like `C++`. | Integrating a programmatic `ALIAS_MAP` translation layer intercepts parsed sets, safeguarding unified blocks (`ci/cd`, `a/b testing`) while expanding compound configurations (`c/c++` into `c`, `c++`) safely before evaluation. |
| <br>Extraneous Data & Edge Cases | A job description and a resume where the local reasoning model fails to extract skills, resulting in raw `<thought>` blocks, empty strings, or default placeholder outputs. | DeepSeek-R1 (1.5B) reasoning tags (`<thought>...</thought>`) leaked directly into string variables when it struggled to find tech stacks, and the model returned literal string failures when there are valid technical skills to be extracted. | Explicit multi-character regex patterns strip stray markdown indicators, and catch logic-leak thinking boundaries. |

### Ensuring Correctness and Reliability

Because generative AI models are inherently probabilistic, the following backend architectural safeguards were implemented to guarantee repeatable execution:

- Network or local context-window choking is mitigated using a 3-attempt linear retry loop (`max_retries=3`) with a 2-second sleep duration to preserve script execution flow during hardware spikes.

- Multi-run testing revealed that while the `ALIAS_MAP` layer perfectly standardizes tokens once they are captured, the underlying local model's extraction pass remains inherently probabilistic. Because small models can occasionally omit or include a specific keyword across consecutive runs on identical text, minor variances can still propagate into the final set-difference calculation. This underscores that downstream deterministic logic can sanitize variations in formatting, but cannot completely override the baseline extraction volatility of a small context window. 

## Limitations

### Model Dependability & Accuracy Trade-offs
The extraction logic was verified exclusively using small-footprint local models (`deepseek-r1:1.5b` and `gemma3:1b`). While highly efficient on constrained consumer hardware, smaller parameter sizes carry a natural trade-off in linguistic reasoning compared to larger cloud models.

### Missing Features & Constraints
**No Experience or Seniority Grading:** The system processes technical skills as binary presence flags. It does not differentiate between junior-level exposure and senior-level experience of the skills, nor does it evaluate the depth of a candidate's professional certifications or non-technical skills.

**Static Local Dataset:** The system evaluates candidates against a static local SQLite database (`jobs.db`) built during the Week 1 data engineering pipeline. It lacks live web-scraping components or dynamic external API integrations to ingest real-time market shifts automatically.

## Architecture Reflections

### Design Choices
The core architectural choice was splitting the pipeline into two distinct scripts: `tag_data.py` (Stage 1) and `find_skill_gaps.py` (Stage 2). 

This separated the probabilistic AI extraction phase from the deterministic evaluation logic. Instead of asking the LLM to both extract and compare the data, which introduces hallucination risks and wastes context window tokens, the LLM is restricted strictly to unstructured-to-structured keyword extraction. The final gap analysis is handed off to local Python set operations, RegEx, and alias mapping layer which ensures 100% mathematical reliability and zero AI hallucination at the evaluation layer.

### Trade-offs

Operating under strict hardware limitations, **simplicity and low resource consumption** were prioritized over raw execution speed.

**In-Memory footprint vs. Network Latency:** Choosing local execution (`gemma3:1b` / `deepseek-r1:1.5b`) completely eliminated external API network dependencies and API cost scaling, but it shifted processing bottlenecks directly to local CPU/RAM performance.

**Transactional Batch Updates vs. Monolithic Writing:** Instead of opening expensive single-row database connections for every individual entry, the pipeline executes model inference and commits updates to `jobs.db` in optimized batches. This batching strategy significantly reduces database I/O overhead and avoids file locks. Crucially, structuring the workflow this way allows for prompt-batching optimizations, which directly minimizes API token usage and stays safely within the restrictive daily rate limits imposed by free-tier or local AI model endpoints.

### Future Improvements & Extensions
If given more time and scalable development resources, the architecture would be extended across four aspects:

**Cloud Integration & Model-Agnostic Flexibility:** The core prompt engine can modified into a generalized provider interface. This would allow the code to easily swap between local hardware backends and robust cloud-based environments, such as Google AI models (Gemini API), making the entire system fully open and adaptable to any commercial or open-source LLM provider.

**Model Context Protocol (MCP) Data Layer:** The direct, raw SQL execution strings inside the application scripts can be moved away in favor of leveraging MCP to call SQL scripts and manage database transactions indirectly. This decouples the core logic from SQLite-specific syntax and improves system security.

**Vector Embedding Graph Integration:** While the hardcoded alias mapping layer successfully handles explicit synonyms (e.g., `React` to `React.js`), the dictionary could be extended into a true vector embedding space or knowledge graph. This would allow the system to implicitly understand conceptual parent-child hierarchies, such as automatically realizing that a candidate with `FastAPI"` exposure implicitly meets a requirement for a generalized `Python Backend` stack.

**Dynamic API Layer:** The static Week 1 `jobs.db` dataset can be transitioned into an automated, live web-scraping queue to keep local job market trends continuously updated in real-time.
