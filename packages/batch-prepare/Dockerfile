FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ /app/shared/

# Copy package-specific code
COPY src/ /app/

# Set Python path to include shared modules
ENV PYTHONPATH=/app

CMD ["python", "/app/batch_prepare_input.py"]