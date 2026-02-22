# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for mysqlclient and SQLite
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    sqlite3 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose port
EXPOSE 5000

# Command
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]