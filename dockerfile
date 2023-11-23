# Use Python 3.11 as base image
FROM python:3.11.6-slim-buster

# Get credentials from launch args
ARG USERNAME
ARG APP_PASSWORD
ARG TIMEOUT=120

# Set environment variables
ENV USERNAME=${USERNAME}
ENV APP_PASSWORD=${APP_PASSWORD}
ENV TIMEOUT=${TIMEOUT}

# Copy files to container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Set working directory
WORKDIR /app

# Run app
CMD ["python", "app.py"]
