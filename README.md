## Description
A container for detecting text in PDF files using tesseract-ocr.
## Build
```
docker build -t ocrmypdf-container .
docker-compose up -d
```
## Preparation
**1. Create directory structure:**
- ~/ocr
- ~/ocr/done
- ~/ocr/error
- ~/ocr/input
- ~/ocr/output

**2. Create a configuration file: ~/ocr/config.txt**

Configure the number of concurrent document processing tasks and set the language by using a code recognized by Tesseract.
```
max_workers = 3
language = pol
```
## Usage
1. Upload PDF files to the input directory.
2. Wait for the program to process the files.
3. Original files will be moved to the done or error directories in case of success or a processing problem.
4. Processed files will be saved in the output directory, accompanied by a .txt file containing the extracted text for each document.
