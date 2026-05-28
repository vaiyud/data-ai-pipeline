# Week 3: System Integration & Application

## Project Overview

The project’s goal is to build and containerize a **full-stack chat application** with a frontend and backend services using Docker. The frontend includes a chat page where user can upload their resume and send messages to the chatbot and the inputs from the user will be sent to the **skill gap detection pipeline** from Week 2 that includes **AI model integration**. The chatbot will then output the skill gaps based on the resume uploaded by the user after comparing with the skills that are popular in job listings extracted from the **data engineering and skill gap detection pipeline.**

## Setup Instructions

This project can be run automatically using **Docker Compose** (recommended) or configured manually using the **uv** package manager for local development.

### 1. Prerequisites

Before getting started, ensure you have the following installed and configured: 

for automatic setup:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

for manual setup:
-  **Python:** `3.14.*`
- **uv:** `0.8.*` package manager

for AI models setup:
- **Ollama:** `0.21.*` (if using local LLMs like `gemma3:1b`) 
- [Google AI API Key](https://aistudio.google.com/) (if using Gemini models) 
---
### 2. Environment Configuration

To manage app settings securely without exposing secrets, you must configure a local `.env` file. A reference template named `.env.example` is provided at the root directory. 

I. Create a copy of the `.env.example` file at the root of the `week_3/` directory and rename it to `.env`: 

    cp .env.example .env

II. Make sure your `.env` file includes the following:

	GOOGLE_API_KEY=<YOUR-GOOGLE-API-KEY-HERE>
	BACKEND_URL=<YOUR-BACKEND-SERVER-URL-HERE>
	DB_PATH=<YOUR-PATH-TO-JOB-DB-FROM-WEEK-2-HERE>
	OLLAMA_HOST=<YOUR-OLLAMA-HOST-URL-HERE>
 
> Warning: DO NOT commit your `.env` containing any `API_KEY` to the repository.

III. Make sure your `.gitignore` file includes the following:

    data/
    **/__pycache__/
    .ruff_cache/
    .venv/
    .env

---
Before setting up automatically or manually, run this command on your terminal.

    git clone https://github.com/vaiyud/data-ai-pipeline.git

### 3. Automatic Setup using Docker Compose

To setup both the frontend and backend service concurrently via Docker Compose:

I. Open your terminal at the project root folder (`week_3/`).

II. Build the target Dockerfile layers and spin up the shared container bridge network:

    docker compose up --build

III. To verify that both containers are running healthy and active on ports `8000` (backend) and `8001` (frontend), open a new terminal window and run the command:

    docker compose ps

IV. Access the web user interface by opening your browser to http://localhost:8001.

---

### 4. Manual Setup via Local

Follow these steps to install configurations across separate terminal sessions.

To setup the **backend service**, on your terminal:

**Navigate to the backend directory:**

    cd week_3/backend

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

**Launch local Uvicorn development server:**

    uv run uvicorn app:app --app-dir src --host 127.0.0.1 --port 8000

---

To setup the **frontend service**, open a new terminal:

**Navigate to the frontend directory:**

    cd week_3/frontend

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

**Launch local frontend interface server:**

    uv run uvicorn main:app --app-dir src --host 127.0.0.1 --port 8001

Then, open http://127.0.0.1:8001 inside your local web browser to begin interacting with the service!

--- 
### Suggestions to configure the `.env` file: 
To make sure you don't break the instructions listed above, make sure you create a file named `.env` inside your `week_3/` root next to your `docker-compose.yml` that looks precisely like this: 

    GOOGLE_API_KEY=<your_google_api_key_here> # from Google AI Studio 
    BACKEND_API_URL=http://backend:8000/chat # for Docker Compose
    BACKEND_API_URL=http://127.0.0.1:8000/chat # for manual setup 
    DB_PATH=data/jobs.db # sample database path 
    OLLAMA_HOST=http://host.docker.internal:11434 # for Docker containers
    OLLAMA_HOST=http://127.0.0.1:11434 # for manual setup

## Usage

Once your services are up and running via Docker Compose or manual local servers, follow these steps to interact with the chat application.

### 1. Accessing the Application Interfaces

Open your preferred web browser and navigate to the following endpoints:

* **Frontend UI Gateway:** [http://localhost:8001](http://localhost:8001) — This is the user-facing chat and upload interface.
* **Backend API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs) — (Optional) Interactive Swagger API documentation to test endpoints manually.

---

### 2. Step-by-Step Execution Workflow

To evaluate a resume against a target job market, follow this sequence:

1.  **Launch the sytem:** Ensure your containers are active. If not, spin them up from the root `week_3/` directory:
    ```bash
    docker compose up
    ```
2.  **Open the webpage:** Navigate to `http://localhost:8001` in your browser.
3.  **Upload your file:**  Locate the upload button on the user interface and browse to select a file (e.g. `resume.txt`).
5.  **Submit for analysis:** Click the **Send** button. The frontend will process the file stream and forward the payload to the backend service.

---

### 3. Expected Inputs & Outputs

To ensure everything is working correctly, verify your input profiles match these expected data shapes:

#### Expected Inputs
* **File Format:** A standard text-extracted resume profiles in `.txt`.
* **Payload Example:** A profile containing technical skills (e.g. *Python, Docker, SQL*) and career history.

#### Expected Outputs
Upon successful processing, the system reads from the evaluation database (`jobs.db`), tracks cross-references, and renders a live response matrix in the chat dashboard:

1.  **Console Logs (Terminal):** Your backend container terminal will log the incoming payload router traffic:
    ```text
    INFO:     172.17.0.1:42654 - "POST /submit-chat HTTP/1.1" 200 OK
    ```
2.  **UI Chatbot Output:** : An explicit list of missing core technologies required by the active job dataset.

## API/Function Reference

This project uses a decoupled microservice architecture where the `frontend` container communicates asynchronously with the `backend` container via an isolated Docker bridge network using the container's service name as the DNS host.

---

### 1. Network Integration

* **Internal Service Route:** `http://backend:8000/chat`
* **Network Driver:** `bridge`
	* Services communicate internally via service-name resolution.
	* Host ports `8000` and `8001` are mapped for external validation.

---

### 2. Backend Endpoint Reference

#### `POST /chat`
Accepts a candidate's resume, saves it to a transient cache folder, reads the tracking metrics from the integrated SQLite database, evaluates inconsistencies, and deletes the transient asset.

* **Content-Type:** `multipart/form-data`
* **Request Payload Parameters:**
  * `chat_file`: `UploadFile (Binary)` — **Required.** The target `.txt` text file containing resume metadata.
  * `user_message`: `string` — *Optional.* Accompanying text instructions or manual string input.

* **Expected Response (`200 OK`):**
  ```json
  {
    "gaps": ["Docker", "Kubernetes", "Redis"]
  }
* **Error Formats:**
    
    -   `400 Bad Request`: Triggered if the `chat_file` parameter or filename payload string is missing/empty.
        
    -   `500 Internal Server Error`: Returns an error payload string if the automation pipeline scripts fail during processing execution.
        
---
### 3. Frontend Core JavaScript Functions (`chat.js`)

#### `chatForm.addEventListener('submit', ...)`

The core submission orchestrator that manages client-to-server data staging operations.

-   **Responsibilities:** Intercepts submission events, reads UI elements, dynamically appends sanitized user text and file chips into the local chat timeline block, serializes data into a `FormData` object wrapper, drops processing text tags onto the viewport, and calls `/submit-chat`.
    

#### `appendSystemBubble(htmlContent)`

Responsible for injecting asymmetric left-aligned feedback wrappers directly into the workspace viewport.

-   **Responsibilities:** Compiles localized timestamps, applies visual shadow classes, appends text payloads dynamically into the DOM tree structure, and executes anchor position resets via `.scrollHeight` modifications to keep updates focused.
    

#### `escapeHTML(str)`

A basic client-side security defense mechanism.

-   **Responsibilities:** Leverages string replacement regex matches to sanitize incoming raw textual nodes (`&`, `<`, `>`, `'`, `"`), converting special symbols into safe HTML entities to neutralize Cross-Site Scripting (XSS) code injections.

## Data/Assumptions

### 1. Data Schema & Contracts

The `frontend` and `backend` microservices exchange structured asynchronous payloads over HTTP multi-part form channels.

* **Frontend to Backend Request:** Passed via `multipart/form-data` containing a `user_message` string and a raw binary file attachment mapped under the key `chat_file`.
* **Backend to Frontend Response (`application/json`):**
  

      { "gaps": ["skill_a", "skill_b", "skill_c"] }

### 2. Core Assumptions & System Constraints

-   **Input File Restrictions:** The file upload mechanism assumes the attached document is a plain text asset (`.txt`) containing unencrypted, extractable resume details.
    
-   **Payload Limits:** User text messages and file streams are processed synchronously; large binary attachments or extreme token counts may hit HTTP gateway timeouts.
    
-   **Logic Simplifications:** The analysis bypasses dynamic interactive conversation tracking. Any individual file submission acts as a discrete execution run.   

### 3. End-to-End Data Flow

The lifecycle of an evaluation request flows sequentially through the architecture:

1.  **Capture:** The user attaches a resume file and submits the form inside their web browser.
    
2.  **Sanitize & Stage:** Client-side JavaScript sanitizes the textual nodes to block XSS, wraps the data inside a `FormData` object, and triggers an asynchronous `POST` to the frontend's `/submit-chat` gateway.
    
3.  **Relay:** The frontend intercepts the request, streams the structural data fields over an isolated Docker network bridge, and forwards them to the backend container endpoint (`/chat`).
    
4.  **Process:** The backend generates a secure transient file clone (`temp_uploads/`), calls the underlying automated script parsing module (`find_skill_gaps`), executes a tracking comparison check against the SQLite engine dataset, and automatically purges the temporary asset directory.
    
5.  **Render:** The backend returns an array string containing the isolated delta metrics. The frontend relays this payload right back to the browser interface, and the DOM automatically mounts left-aligned system response bubbles onto the user viewport.

## Testing

The system components were validated using user-interface simulation blocks to ensure correct microservice routing over the Docker bridge network.

### Frontend & Integration Testing:

End-to-end communication constraints were validated across common user behaviors to ensure proper state management and network fail-safes.
| Component Tested | Action/Scenario | Test Case Objective | Expected Outcome/Mitigation |
|--|--|--|--|
| **Frontend UI** | Submit form empty | Block redundant payloads | Form processing stops instantly; DOM does not append blank chat blocks. |
| **Frontend UI** | Submit text prompt _without_ a file | Warn user of file constraint | System bubble renders: _"Please upload a resume file..."_ |
| **Frontend UI** | Select file via file explorer | Mount UI visual indicators | Hides default state; unhides white preview container displaying exact filename. |
| **Integration** | Submit valid file + message payload | Verify Docker bridge stability | File bytes stream successfully across containers; returns calculated list from DB. |
| **Network Fail-Safe** | Kill backend service container | Test `httpx.ConnectError` handling | Client catches network timeout and throws a descriptive `503 Service Unavailable` message bubble. |

## Limitations

This system is a localized development prototype focused on validating dockerized microservice orchestration. It has the following boundaries and known constraints:

### 1. Functional & Feature Gaps
* **Volatile Session State:** There is no user authentication, multi-user isolation, or persistent database layer for the communication timeline. Refreshing the browser tab completely clears the ongoing chat log.

* **No Dynamic Conversational Memory:** The system operates as a single-turn pipeline. The script evaluates the currently uploaded document in isolation and does not retain contextual memory of previously submitted prompts or files within the same session.

### 2. Processing & Performance Constraints
* **Synchronous File Bottlenecks:** File ingestion reads the multi-part data stream synchronously. Processing massive plain text assets or handling multiple concurrent requests will block execution threads, occasionally triggering `504 ReadTimeout` network faults.

* **Text-Only Ingestion:** The current parsing pipeline does not native-process binary document shapes like formatted PDFs or Word documents (`.docx`). Files must be pre-extracted or uploaded as raw plain-text templates (`.txt`).

### 3. Model Accuracy & Data Trade-offs
* **Deterministic Matching:** The skill gap logic relies on direct token alignment against the local SQLite dataset. If a resume lists a valid synonym or alternative phrasing for a technology that isn't exact, the pipeline may flag it as an artificial missing gap.

* **Resource Hallucinations:** Smaller local models (e.g., `gemma3:1b`) run fast on limited local development hardware but trade off reasoning accuracy, occasionally generating overly generalized or repetitive learning roadmaps compared to cloud-tier models.

## Architecture Reflections

### Design Choices

* **Decoupled Microservices:** Separating the user interface (`frontend`) from the logic engine (`backend`) ensures that changes to UI aesthetics or styling do not impact the core data-processing stability. It establishes an asynchronous framework where the frontend handles user interactions while the backend scales independent AI pipelines.

* **Containerization with Docker:** Developing across different environments often introduces dependency conflicts. Containerizing each service ensures absolute environmental parity. By locking down the runtime to an explicit Python base image, the application runs identically on host Windows machines, inside WSL, or across isolated cloud networks without relying on native system configurations.

### Trade-offs

* **Deployment Ease vs. Performance Optimization:** This project prioritized immediate, zero-config reproducibility using `docker compose` over a highly distributed, production-grade network architecture. Using an isolated bridge network simplifies orchestration but passes file payloads synchronously through two distinct software boundaries, adding minor latency compared to a single-process monolithic deployment.

* **Interface Simplicity vs. Advanced Features:** The choice of clean, vanilla client-side JavaScript inside a single-page chat dashboard was favored over a heavy frontend framework (like React or Vue). This kept development fast and focused entirely on validating the multi-container data flow, trading off multi-user state persistence and interactive conversational flexibility for low-overhead simplicity.

### Improvements

If given more development iterations, the architecture would be extended across three key areas:

1. **Dynamic Runtime Model Selection:** Modify the frontend UI to include an interactive model selection dropdown. This would allow users to dynamically pass the chosen model identifier string (e.g. swapping from cloud-based `gemini-2.5-flash` to local `deepseek-r1:1.5b`) within the HTTP request metadata, updating the backend processing path instantly on the fly without changing code files or restarting services.

2. **Interactive Database Analytics & Dashboards:** Integrate `Chart.js` directly into the user interface to visually map out metrics from the underlying historical job dataset. This would provide real-time dashboard analytics—such as categorical pie charts, job market distribution plots, and an active keyword search utility bar which allow users to cross-examine database records directly from their browser.

4. **Fully Self-Contained Ollama Service Container:** Add the official `ollama/ollama` base image straight into the `docker-compose.yml` service cluster to eliminate external, local application dependencies. For compatible target host environments, hardware passthrough flags would be added to grant the container direct GPU acceleration access.
