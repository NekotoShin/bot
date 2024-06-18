# syntax=docker/dockerfile:1
FROM python:3.10-alpine

# Set the working directory
WORKDIR /app

# Create environment variables
ENV token=your_token_here

# Install system dependencies
RUN apk update
RUN apk add --no-cache bash build-base cargo gcc git g++ libffi-dev linux-headers musl-dev openssl-dev perl rust

# Install the required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining files
COPY config/ config/
COPY src/ src/
COPY start.py .

# Run the application
CMD ["python", "start.py"]
