FROM python:3.11-slim

WORKDIR /app

# Copy only DjangoBackend folder into the container
COPY ./DjangoBackend /app

# Install PostgreSQL client (for health checks or manage.py db commands)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt inside DjangoBackend
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make sure entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
