## Description
A container for text detection in PDF files using OCRMyPDF and Tesseract-OCR.
## Preparation
**1. Create directory structure**
```
mkdir ~/ocr
mkdir ~/ocr/done
mkdir ~/ocr/error
mkdir ~/ocr/input
mkdir ~/ocr/output
```
**2. Create log file**
```
touch ~/ocr/ocr.log
```
**3. Create configuration file**
```
vi /ocr/config.txt
```
```
# Number of documents being processed at the same time
max_workers = 2

# Language(s) of the file to be OCRed (see tesseract --list-langs for all language packs installed in your system). Use -l eng+deu for multiple languages.
language = pol

# For input image instead of PDF, use this DPI instead of file's.
image_dpi = 300

# Control  how  PDF  is optimized after processing:
# 0 - do not optimize; 1 - do safe, lossless optimizations (default); 2 - do some lossy optimizations; 3 - do aggressive
optimize = 1

# Set Tesseract OCR engine mode: 0 - original Tesseract only; 1 - neural nets LSTM only; 2 - Tesseract + LSTM; 3 - default.
tesseract-oem = 2
```

**4. Setup language**

Set your language in the dockerfile

## Build and run the container
```
docker build -t ocrmypdf-container .
docker run -d --name ocrmypdf -v ~/ocr:/app/data --restart unless-stopped ocrmypdf-container:latest
```
## Usage
1. Upload PDF files to the input directory.
2. Wait for the program to process the files.
3. Original files will be moved to the done or error directories in case of success or a processing problem.
4. Processed files will be saved in the output directory, accompanied by a .txt file containing the extracted text for each document.
