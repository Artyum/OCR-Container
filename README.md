## Description
A container for text detection in PDF files using OCRMyPDF and Tesseract-OCR.

### Additional features:
- Convertion PNG and JPG to PDF
- Merge multiple files into one
- Extract text to a TXT file

## Usage
1. Upload PDF files to the input directory.
2. Wait for the program to process the files.
3. Original files will be moved to the done or error directories in case of success or a processing problem.
4. Processed files will be saved in the output directory, accompanied by a .txt file containing the extracted text for each document.

JPG and PNG files are automatically converted to PDF.  
To merge multiple files, place them in the combine directory. The merging occurs in alphabetical order.

## Preparation
**1. Create files and directory structure**
```
mkdir ~/ocr
mkdir ~/ocr/combine
mkdir ~/ocr/done
mkdir ~/ocr/error
mkdir ~/ocr/input
mkdir ~/ocr/output
```
![image](https://github.com/user-attachments/assets/39f4f18f-c6b9-417c-b0a8-b62eb642b224)

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

**4. Setup language in the dockerfile**

##### 1. Install the required language packs:
```
RUN apt-get update && apt-get install -y \
  ocrmypdf \
  tesseract-ocr \
  tesseract-ocr-pol \
  #tesseract-ocr-* \
  (...)
```
##### 2. Download the appropriate language model file
```
RUN wget https://raw.githubusercontent.com/tesseract-ocr/tessdata/main/pol.traineddata -O /usr/share/tesseract-ocr/5/tessdata/pol.traineddata
```

## Build and run the container
```
docker build -t ocrmypdf-container .
docker run -d --name ocrmypdf -v ~/ocr:/app/data --restart unless-stopped ocrmypdf-container:latest
```
