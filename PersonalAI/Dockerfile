# PersonalAI Docker Container
# Production-ready containerized deployment

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY ../requirements.txt ./parent_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r parent_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /root/.personalai/memory \
    /root/.personalai/state \
    /root/.personalai/logs \
    /app/data

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PERSONALAI_ENV=production

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "from core.monitoring import get_monitoring_system; m=get_monitoring_system(); status=m.get_system_status(); exit(0 if status['overall_status']=='healthy' else 1)"

# Expose ports (if needed for web interface)
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "run.py", "enhanced"]
