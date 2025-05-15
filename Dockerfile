FROM python:3.9-slim
# Set environment variables to prevent prompts during installation
WORKDIR /app
# Install curl for healthcheck and git for GitPython
RUN apt-get update && apt-get install -y curl git
# Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the application files
COPY . /app
# Create necessary directories
RUN mkdir -p evidence sdt_output logs
EXPOSE 8000
# Set the Python path correctly
ENV PYTHONPATH=/app
# Use the correct module path
CMD ["uvicorn", "sdt_interface:app", "--host", "0.0.0.0", "--port", "8000"]