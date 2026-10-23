# Use the official lightweight Python 3.12 image as the base
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Install system-level build tools (gcc) for compiling packages safely
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/api/lists/*

# Copy the backend requirements file and install Python dependencies
COPY requirements-backend.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend project files into the container
COPY . .

# Expose port 8000 for network traffic
EXPOSE 8000

# Define the default command to run the FastAPI server via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]