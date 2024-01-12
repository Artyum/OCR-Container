FROM python:3.8-slim

# Install system dependencies for OCRmyPDF and file monitoring tools
RUN apt-get update && apt-get install -y \
  ocrmypdf \
  tesseract-ocr \
  tesseract-ocr-pol \
  poppler-utils \
  pdftk \
  vim \
  inotify-tools \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files to container
COPY ocr.py /app/

# Create and activate Python virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir watchdog

# Command to be executed when container starts
CMD ["python", "ocr.py"]
