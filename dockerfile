FROM python:3.8-slim

# Install system dependencies for OCRmyPDF and file monitoring tools
RUN apt-get update && apt-get install -y \
  ocrmypdf \
  tesseract-ocr \
  tesseract-ocr-* \
  poppler-utils \
  pdftk \
  vim \
  inotify-tools

RUN apt-get install -y \
  git \
  zlib1g-dev \
  autotools-dev \
  make \
  g++ \
  automake \
  libtool \
  libleptonica-dev \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone and build jbig2enc
RUN git clone https://github.com/agl/jbig2enc \
  && cd jbig2enc \
  && ./autogen.sh \
  && ./configure && make \
  && make install

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
