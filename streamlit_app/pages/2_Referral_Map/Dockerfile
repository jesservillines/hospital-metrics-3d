FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create data directory and copy data files first
RUN mkdir -p /app/data
COPY data/*.csv /app/data/

# Copy the models directory
COPY models ./models

# Copy the application code
COPY Home.py .
COPY pages ./pages
COPY *.py .
COPY *.yaml .

# Add debug commands to verify file structure
RUN echo "Listing /app directory:" && ls -la /app && \
    echo "Listing /app/data directory:" && ls -la /app/data && \
    echo "Listing /app/pages directory:" && ls -la /app/pages

# Expose the port Streamlit runs on
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Create a healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the application
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
