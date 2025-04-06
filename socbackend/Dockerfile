FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including libffi-dev
RUN apt-get update && apt-get install -y \
  build-essential \
  libffi-dev \
  pkg-config \
  wget \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN python -m venv /opt/venv && \
  /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
  /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment path
ENV PATH="/opt/venv/bin:$PATH"

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "--config", "gunicorn.conf.py", "socbackend.wsgi:application"] 