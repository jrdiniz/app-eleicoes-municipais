# Use the official Python image from the Docker Hub
FROM ubuntu:22.04

# Set environment variables to non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /htdocs

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

WORKDIR /htdocs/app/static
RUN npm install

# Change to root directory
WORKDIR /htdocs

# Expose the port that the Flask app runs on
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app
ENV FLASK_DEBUG=False
ENV FLASK_CONFIG_FILE=config.DevelopmentConfig
ENV SECRET_KEY=<your-secret-key>

# Command to run the Flask application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]