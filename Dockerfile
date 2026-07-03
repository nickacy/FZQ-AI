# FZQ-AI · V24 Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose API port
EXPOSE 8000

# Start FastAPI (Entry Layer V24)
CMD ["uvicorn", "src.fzq_ai.ui.web_app:app", "--host", "0.0.0.0", "--port", "8000"]
