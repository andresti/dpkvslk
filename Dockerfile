FROM python:3.12-slim

WORKDIR /app

# Install build essentials for llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src src

RUN mkdir -p models uploads

EXPOSE 5001

CMD ["python", "src/app.py"]

