FROM python:3.11-slim

WORKDIR /my_app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8000
ENV LOG_LEVEL=info
ENV DEV_MODE=production

# Expose the application port
EXPOSE ${PORT}

# Use array syntax for CMD to avoid shell parsing issues
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
