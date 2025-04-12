# Use the official Python image.
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set the environment variable to tell Flask it's running in production
ENV FLASK_ENV=production

# Set the port (Cloud Run expects the app to listen on $PORT)
ENV PORT=8080

# Expose the port (not strictly required by Cloud Run, but good practice)
EXPOSE $PORT

# Start the Flask app
CMD ["python", "app.py"]