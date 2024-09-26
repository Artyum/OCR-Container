# Use the latest Ubuntu LTS image (22.04)
FROM ubuntu:22.04

# Set environment variable to avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update packages and install tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    gnupg \
    wget \
    lsb-release \
    ca-certificates \
    git \
    build-essential \
    autotools-dev \
    automake \
    libtool \
    libtiff-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libleptonica-dev \
    libjbig2dec0-dev \
    && rm -rf /var/lib/apt/lists/*

# Add the official Tesseract OCR PPA to install version 5
RUN add-apt-repository ppa:alex-p/tesseract-ocr-devel \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-all \
    ocrmypdf \
    poppler-utils \
    pdftk \
    unpaper \
    inotify-tools \
    pngquant \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install jbig2enc from source
RUN git clone https://github.com/agl/jbig2enc.git /tmp/jbig2enc \
    && cd /tmp/jbig2enc \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/jbig2enc

# Set the working directory
WORKDIR /app

# Download trained models with fast variant of the "best" LSTM models + legacy models
# Save in /usr/share/tesseract-ocr/5/tessdata/
RUN git clone https://github.com/tesseract-ocr/tessdata.git \
    && mv -f tessdata/*traineddata /usr/share/tesseract-ocr/5/tessdata/ \
    && mv -f tessdata/script /usr/share/tesseract-ocr/5/tessdata/ \
    && rm -rf tessdata

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir watchdog img2pdf

# Copy application files to the container
COPY ocr-machine.py /app/

# Set the default command (can be overridden in K8S)
CMD ["python3", "ocr-machine.py"]
