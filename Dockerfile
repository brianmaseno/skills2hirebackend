FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install djongo separately with --no-deps to avoid sqlparse version conflict
# djongo requires sqlparse==0.2.4 but Django requires sqlparse>=0.3.1
# Using --no-deps and relying on Django's sqlparse works in practice
RUN pip install djongo==1.3.6 --no-deps

# Copy project
COPY . .

# Create media and static directories
RUN mkdir -p media staticfiles

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
