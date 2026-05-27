# official base image
FROM python:3.14.4-bookworm

# working directory inside the container
WORKDIR /week_3/frontend

# copy files from workspace to container
COPY . .

# uv configuration
RUN curl -LsSf https://astral.sh/uv/0.8.8/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# environment configurations
RUN uv venv
# RUN uv add fastapi httpx jinja2 uvicorn python-dotenv ruff=="0.15.*"
# RUN uv pip install "fastapi[standard]"
RUN uv sync --frozen

# the port the app runs on
EXPOSE 8001

# commands to run the application
ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["--app-dir", "src", "--host", "0.0.0.0", "main:app", "--port", "8001"] 