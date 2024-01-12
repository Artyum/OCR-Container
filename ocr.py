import time
import logging
import subprocess
import os
import shutil
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

    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None

        elif event.src_path.endswith('.pdf'):
            # Process the PDF file
            try:
                logging.info(f"Received new file: {event.src_path}")
                input_path = event.src_path
                ocr_output_path = os.path.join(Watcher.DIRECTORY_OUTPUT, os.path.basename(event.src_path))
                text_output_path = os.path.join(Watcher.DIRECTORY_OUTPUT, os.path.splitext(os.path.basename(event.src_path))[0] + '.txt')

                with open('/app/data/ocrmypdf.log', 'a') as log_file:
                    # Extract text from the PDF using OCRmyPDF with the specified options
                    result = subprocess.call(['ocrmypdf', '--image-dpi', '300', '--optimize', '3', '--output-type', 'pdfa', '--redo-ocr', '--tesseract-oem', '1', '-l', 'pol', input_path, ocr_output_path],
                                    stdout=log_file, stderr=subprocess.STDOUT)

                    # Extract text from the processed PDF using pdftotext if OCR is successful
                    if result == 0:
                        subprocess.call(['pdftotext', '-layout', ocr_output_path, text_output_path],
                                        stdout=log_file, stderr=subprocess.STDOUT)
                        shutil.move(input_path, Watcher.DIRECTORY_DONE)
                        logging.info(f"Processed and moved to done: {event.src_path}")
                    else:
                        shutil.move(input_path, Watcher.DIRECTORY_ERROR)
                        logging.error(f"Processing failed, moved to error: {event.src_path}")

            except Exception as e:
                shutil.move(input_path, Watcher.DIRECTORY_ERROR)
                logging.error(f"Error processing file {event.src_path}: {e}")

if __name__ == '__main__':
    w = Watcher()
    w.run()
