FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv and dependencies using --system flag
COPY requirements.txt ./
RUN pip install uv && uv pip install --system -r requirements.txt

# Copy app code
COPY . .

# Expose port for Flet
EXPOSE 8000

# Start the app
CMD ["python", "src/main.py"]
