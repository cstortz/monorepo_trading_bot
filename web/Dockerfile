FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy web files
COPY web /app/web

# Set working directory to web
WORKDIR /app/web

# Expose port
EXPOSE 5080

# Run the server
CMD ["python", "server.py"]

