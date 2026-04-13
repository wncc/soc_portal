# # Use Python 3.12 slim image
# FROM python:3.12-slim

# # Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Set work directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update \
#   && apt-get install -y --no-install-recommends \
#   build-essential \
#   libpq-dev \
#   libffi-dev \
#   pkg-config \
#   && apt-get clean \
#   && rm -rf /var/lib/apt/lists/*

# # Install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project
# COPY . .

# # Collect static files
# RUN python manage.py collectstatic --noinput

# # Run gunicorn
# CMD ["gunicorn", "--config", "gunicorn.conf.py", "socbackend.wsgi:application"] 


# Use Python 3.12 slim image
FROM python:3.12-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Start app:
# 1) apply migrations
# 2) collect static files
# 3) run gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --config gunicorn.conf.py socbackend.wsgi:application"]