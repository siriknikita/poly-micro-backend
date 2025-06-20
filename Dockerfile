FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    RELOAD=False \
    ENV=production \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    CACHE_ENABLED=True

# Install system dependencies - this layer changes rarely
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    redis-tools \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies - this layer only rebuilds if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# First copy core modules that need to be available early in import process
COPY ./app/core/enum_compat.py ./app/core/enum_compat.py
COPY ./app/__init__.py ./app/__init__.py

# Then copy main application code
COPY ./app ./app
COPY ./run.py .
COPY ./.env* ./
COPY ./entrypoint.sh .

# Then copy the rest of the files
COPY . .

# Make entrypoint executable
RUN chmod +x ./entrypoint.sh

# Expose the port
EXPOSE 8000

# Use entrypoint script to handle startup tasks
ENTRYPOINT ["/app/entrypoint.sh"]
