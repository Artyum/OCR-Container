import time
import logging
import subprocess
import os
import shutil
import concurrent.futures
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(filename='/app/data/ocrmypdf.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

class Watcher:
    DIRECTORY_TO_WATCH = "/app/data/input"  # Directory to watch for new PDF files
    DIRECTORY_OUTPUT = "/app/data/output"   # Directory to save processed PDFs and extracted text
    DIRECTORY_DONE = "/app/data/done"       # Directory to move processed PDFs after successful processing
    DIRECTORY_ERROR = "/app/data/error"     # Directory to move PDFs that fail to process
    
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)   # Wait for 5 seconds between checking for file changes
        except Exception as e:
            self.observer.stop()
            logging.error(f"Observer stopped due to error: {e}")

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    def __del__(self):
        self.executor.shutdown(wait=True)

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.pdf'):
            return None
        self.executor.submit(self.process_pdf, event.src_path)

    @staticmethod
    def process_pdf(file_path):
        try:
            logging.info(f"Received new file: {file_path}")
            ocr_output_path = os.path.join(Watcher.DIRECTORY_OUTPUT, os.path.basename(file_path))
            text_output_path = os.path.join(Watcher.DIRECTORY_OUTPUT, os.path.splitext(os.path.basename(file_path))[0] + '.txt')

            # Check if the output file already exists, and delete it if it does
            if os.path.exists(ocr_output_path):
                os.remove(ocr_output_path)
                os.remove(text_output_path)
            
            # Extract text from the PDF using OCRmyPDF
            result = subprocess.call(['ocrmypdf', '--image-dpi', '300', '--optimize', '3', '--output-type', 'pdfa', '--redo-ocr', '--tesseract-oem', '1', '-l', 'pol', file_path, ocr_output_path])

            # Extract text from the processed PDF using pdftotext if OCR is successful
            if result == 0:
                subprocess.call(['pdftotext', '-layout', ocr_output_path, text_output_path])
                shutil.move(file_path, Watcher.DIRECTORY_DONE)
                logging.info(f"Processed and moved to done: {file_path}")
            else:
                shutil.move(file_path, Watcher.DIRECTORY_ERROR)
                logging.error(f"Processing failed, moved to error: {file_path}")

        except Exception as e:
            shutil.move(file_path, Watcher.DIRECTORY_ERROR)
            logging.error(f"Error processing file {file_path}: {e}")

if __name__ == '__main__':
    logging.info(f"START")
    w = Watcher()
    w.run()
