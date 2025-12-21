# PersonalAI Docker Container
# Production-ready container voor PersonalAI

FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Metadata
LABEL maintainer="PersonalAI"
LABEL description="Personal AI Assistant powered by RoboBrain 2.0"
LABEL version="1.0"

# Omgevingsvariabelen
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda

# Installeer system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    wget \
    curl \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Maak symlink voor python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Werk directory
WORKDIR /app

# Kopieer requirements
COPY requirements.txt /app/PersonalAI/requirements.txt
COPY ../requirements.txt /app/requirements.txt

# Installeer Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir -r /app/PersonalAI/requirements.txt

# Kopieer RoboBrain code
COPY ../inference.py /app/inference.py
COPY ../assets /app/assets

# Kopieer PersonalAI applicatie
COPY . /app/PersonalAI

# Maak data directories
RUN mkdir -p /app/PersonalAI/data/cache \
             /app/PersonalAI/data/memory \
             /app/result

# Set permissions
RUN chmod +x /app/PersonalAI/main.py

# Working directory voor runtime
WORKDIR /app/PersonalAI

# Expose poorten
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python main.py status || exit 1

# Default command (kan overridden worden)
CMD ["python", "main.py", "telegram"]

# Volume voor persistent data
VOLUME ["/app/PersonalAI/data", "/root/.cache/huggingface"]
