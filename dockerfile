FROM python:3.8-slim

# Install system dependencies for OCRmyPDF and file monitoring tools
RUN apt-get update && apt-get install -y \
  ocrmypdf \
  tesseract-ocr \
  tesseract-ocr-pol \
  #tesseract-ocr-* \
  poppler-utils \
  pdftk \
  vim \
  inotify-tools \
  pngquant \
  wget

RUN apt-get install -y \
  git \
  zlib1g-dev \
  autotools-dev \
  make \
  g++ \
  automake \
  libtool \
  libleptonica-dev \
  supervisor \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone and build jbig2enc
RUN git clone https://github.com/agl/jbig2enc \
  && cd jbig2enc \
  && ./autogen.sh \
  && ./configure && make \
  && make install

# Download OCR model
# https://github.com/tesseract-ocr

# Best (most accurate) trained LSTM models.
#RUN wget https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/pol.traineddata -O /usr/share/tesseract-ocr/5/tessdata/pol.traineddata

# Trained models with fast variant of the "best" LSTM models + legacy models
RUN wget https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/pol.traineddata -O /usr/share/tesseract-ocr/5/tessdata/pol.traineddata

# Create and activate Python virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir watchdog img2pdf

# Copy files to container
COPY ocr.py /app/
COPY combine.py /app/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Command to be executed when container starts
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
