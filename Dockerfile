# =============================================================================
# CV Extractor - Docker Configuration
# =============================================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure app directory is a Python package
RUN touch app/__init__.py

# Create necessary directories
RUN mkdir -p \
    data/input \
    data/uploads \
    data/outputs \
    data/results \
    data/ground_truth

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/web
ENV HOST=0.0.0.0
ENV PORT=5000
ENV DEBUG=False

# Create startup script
RUN echo '#!/bin/bash\ncd /app\nexport PYTHONPATH=/app:$PYTHONPATH\npython web/app.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/')" || exit 1

# Command to run the application
CMD ["/app/start.sh"]