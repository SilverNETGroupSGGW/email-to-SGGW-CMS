# Use Python 3.11 as base image
FROM python:3.11-slim

# Copy files to container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Set working directory
WORKDIR /app

# Run app
CMD ["python", "main.py"]
