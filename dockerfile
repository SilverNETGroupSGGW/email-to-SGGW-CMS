# Use Python 3.11 as base image
FROM python:3.11-slim

# Get credentials from launch args
ARG USERNAME
ARG APP_PASSWORD

# Set environment variables
ENV USERNAME=${USERNAME}
ENV APP_PASSWORD=${APP_PASSWORD}
ENV TIMEOUT=${TIMEOUT}
ENV IMAP_SERVER=${IMAP_SERVER}

# Copy files to container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Set working directory
WORKDIR /app

# Run app
CMD ["python", "main.py"]
