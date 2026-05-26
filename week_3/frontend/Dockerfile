# official base image
FROM python:3.14.4-bookworm

# working directory inside the container
WORKDIR /week_3/frontend

# copy the application dependecies files
# COPY . .
COPY uv.lock pyproject.toml ./

# install dependencies
RUN curl -LsSf https://astral.sh/uv/0.8.8/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv venv
# RUN source .venv/bin/activate
# RUN uv add fastapi jinja2 uvicorn python-dotenv
# RUN uv add ruff=="0.15.*"
RUN uv sync --frozen
# RUN apt install python3-fastapi
# RUN uv pip install "fastapi[standard]"
# RUN uvicorn --app-dir src main:app

# the port the app runs on
EXPOSE 8000

ENTRYPOINT ["uv", "run", "uvicorn"]

# commands to run the application
CMD ["--app-dir", "src", "--host", "0.0.0.0", "main:app"] 