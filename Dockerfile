FROM python:3.10-slim

WORKDIR /app

# Copy all your files into the container
COPY . .

# Install dependencies using uv
RUN pip install uv
RUN uv sync

# Expose the specific port Hugging Face requires
EXPOSE 7860

# Start the server on port 7860
CMD ["uv", "run", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]