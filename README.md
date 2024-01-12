# Description
A container for detecting text in PDF files using tesseract-ocr.
## Build
```
docker build -t ocrmypdf-container .
docker-compose up -d
```
## Preparation
Directory structure used by the program:
- ~/ocr
- ~/ocr/done
- ~/ocr/error
- ~/ocr/input
- ~/ocr/output
## Usage
1. Upload PDF files to the input directory.
2. Wait for the program to process the files.
3. Processed files will be saved in the output directory.
4. Original files will be moved to the done or error directories in case of success or a processing problem.
