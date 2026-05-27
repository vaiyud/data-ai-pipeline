# official base image
FROM python:3.14.4-bookworm

# working directory inside the container
WORKDIR /app

# copy files from workspace to container
COPY . .

# uv configuration
RUN curl -LsSf https://astral.sh/uv/0.8.8/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# environment configurations
RUN uv venv
RUN uv sync --frozen

# the port the app runs on
EXPOSE 8000

# commands to run the application
ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["--app-dir", "src", "--host", "0.0.0.0", "app:app", "--port", "8000"]