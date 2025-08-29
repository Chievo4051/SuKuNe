# Dockerfile untuk SeKuNe Backend
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    sqlite \
    sqlite-dev \
    && rm -rf /var/cache/apk/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p src/static/uploads && \
    chmod 755 src/static/uploads

# Create non-root user for security
RUN adduser -D -s /bin/sh sekune && \
    chown -R sekune:sekune /app

# Switch to non-root user
USER sekune

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Run the application
CMD ["python", "src/main.py"]

