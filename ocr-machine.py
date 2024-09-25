import time
import logging
import subprocess
import os
import shutil
import concurrent.futures
import signal
import sys
import img2pdf
import threading
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from threading import Timer

# ================================
# Global Directory Definitions
# ================================

# Directories for the Watcher
WATCHER_DIRECTORIES = {
    "to_watch": "/app/data/input",     # Directory to watch for new PDF files
    "output": "/app/data/output",      # Directory to save processed PDFs and extracted text
    "done": "/app/data/done",          # Directory to move processed PDFs after successful processing
    "error": "/app/data/error"         # Directory to move PDFs that fail to process
}

# Directories for the CombineWatcher
COMBINE_WATCHER_DIRECTORIES = {
    "to_watch": "/app/data/combine",    # Directory to watch for files to combine
    "output": "/app/data/input",        # Directory to save combined PDFs
    "done": "/app/data/done"            # Directory to move combined PDFs after successful processing
}

# ================================
# Utility Functions for Directories
# ================================

def delete_directories(directories):
    """
    Deletes the specified directories along with their contents.

    Args:
        directories (dict): A dictionary of directory paths to delete.
    """
    for key, directory in directories.items():
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
            except Exception as e:
                logging.error(f"Failed to delete directory '{directory}': {e}")

def create_directories(directories):
    """
    Creates the specified directories. If a directory already exists, it will not raise an error.

    Args:
        directories (dict): A dictionary of directory paths to create.
    """
    for key, directory in directories.items():
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create directory '{directory}': {e}")

# ================================
# Configuration Class
# ================================

class Config:
    max_workers = 2     # default number of concurrent workers
    language = 'pol'    # default language
    image_dpi = 300     # default DPI value
    optimize = 3        # default optimize level
    tesseract_oem = 2   # default tesseract-oem

    @staticmethod
    def load_config():
        try:
            with open('/app/data/config.txt', 'r') as file:
                for line in file:
                    name, value = line.partition("=")[::2]
                    if name.strip() == 'max_workers':
                        Config.max_workers = int(value.strip())
                    elif name.strip() == 'language':
                        Config.language = value.strip()
                    elif name.strip() == 'image_dpi':
                        Config.image_dpi = int(value.strip())
                    elif name.strip() == 'optimize':
                        Config.optimize = int(value.strip())
                    elif name.strip() == 'tesseract-oem':
                        Config.tesseract_oem = int(value.strip())
        except Exception as e:
            logging.error(f"Error loading config file: {e}")

        logging.info("Configuration loaded:")
        logging.info(f" - max_workers={Config.max_workers}")
        logging.info(f" - language={Config.language}")
        logging.info(f" - image_dpi={Config.image_dpi}")
        logging.info(f" - optimize={Config.optimize}")
        logging.info(f" - tesseract-oem={Config.tesseract_oem}")

# ================================
# Watcher Class
# ================================

class Watcher:
    def __init__(self):
        # Initialize directories by deleting and recreating them
        logging.info(f"Initialize directories")
        delete_directories(WATCHER_DIRECTORIES)
        create_directories(WATCHER_DIRECTORIES)
        
        self.observer = PollingObserver(timeout=5)
        Config.load_config()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, WATCHER_DIRECTORIES["to_watch"], recursive=True)
        self.observer.start()
        logging.info(f"Started watching directory: {WATCHER_DIRECTORIES['to_watch']}")
        try:
            self.observer.join()
        except Exception as e:
            self.observer.stop()
            logging.error(f"Observer stopped due to error: {e}")

    def stop(self):
        self.observer.stop()
        self.observer.join()

# ================================
# Handler Class for Watcher
# ================================

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=Config.max_workers)

    def __del__(self):
        self.executor.shutdown(wait=True)

    def on_created(self, event):
        if not event.src_path.endswith('.pdf'):
            logging.info(f"Ignored non-PDF file: {event.src_path}")
            return

        if event.is_directory:
            return

        self.executor.submit(self.process_pdf, event.src_path)

    @staticmethod
    def process_pdf(file_path):
        logging.info(f"Processing new file: {file_path}")
        ocr_output_path = os.path.join(WATCHER_DIRECTORIES["output"], os.path.basename(file_path))
        text_output_path = os.path.join(WATCHER_DIRECTORIES["output"], os.path.splitext(os.path.basename(file_path))[0] + '.txt')
        done_path = os.path.join(WATCHER_DIRECTORIES["done"], os.path.basename(file_path))
        error_path = os.path.join(WATCHER_DIRECTORIES["error"], os.path.basename(file_path))

        # Clean old files
        for path in [ocr_output_path, text_output_path, done_path, error_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logging.error(f"Failed to remove existing file '{path}': {e}")

        command = [
            'ocrmypdf',
            '--image-dpi', str(Config.image_dpi),
            '--optimize', str(Config.optimize),
            '--tesseract-oem', str(Config.tesseract_oem),
            '--clean',
            '--output-type', 'pdfa-2',
            '--redo-ocr',
            '-l', str(Config.language),
            file_path,
            ocr_output_path
        ]
        logging.info(f"Executing command: {' '.join(command)}")
        
        # Extract text from the PDF using OCRmyPDF
        try:
            # Perform OCR using OCRmyPDF
            result = subprocess.call(command)

            # Check if OCRmyPDF was successful (result == 0)
            if result != 0:
                # If OCR failed, log the error with the exit code
                logging.error(f"OCRmyPDF failed with exit code {result} for file {file_path}")
                shutil.move(file_path, Watcher.DIRECTORIES_ERROR)
            else:
                # If OCR succeeded, proceed to extract text from the PDF
                subprocess.call(['pdftotext', '-layout', ocr_output_path, text_output_path])
                shutil.move(file_path, Watcher.DIRECTORIES_DONE)
                logging.info(f"Processed and moved to done: {file_path}")

        except subprocess.CalledProcessError as e:
            # Capture and log details when OCRmyPDF throws a CalledProcessError
            logging.error(f"Error during OCR processing of file {file_path}. Command: {e.cmd}, Return code: {e.returncode}, Output: {e.output}")
            shutil.move(file_path, Watcher.DIRECTORIES_ERROR)

        except Exception as e:
            # Handle any other general errors and log them with details
            shutil.move(file_path, Watcher.DIRECTORIES_ERROR)
            logging.error(f"General error processing file {file_path}: {str(e)}")

# ================================
# CombineWatcher Class
# ================================

class CombineWatcher:
    def __init__(self):
        # Initialize directories by deleting and recreating them
        delete_directories(COMBINE_WATCHER_DIRECTORIES)
        create_directories(COMBINE_WATCHER_DIRECTORIES)
        
        self.observer = PollingObserver(timeout=5)

    def run(self):
        event_handler = CombineHandler()
        self.observer.schedule(event_handler, COMBINE_WATCHER_DIRECTORIES["to_watch"], recursive=False)
        self.observer.start()
        logging.info(f"Started watching directory: {COMBINE_WATCHER_DIRECTORIES['to_watch']}")
        try:
            self.observer.join()
        except Exception as e:
            self.observer.stop()
            logging.error(f"Observer stopped due to error: {e}")

    def stop(self):
        self.observer.stop()
        self.observer.join()

# ================================
# Handler Class for CombineWatcher
# ================================

class CombineHandler(FileSystemEventHandler):
    def __init__(self):
        self.timer = None
        self.wait_time = 5  # Waiting time for more files
        self.files_to_process = []
        self.lock = threading.Lock()

    def on_created(self, event):
        try:
            if not event.is_directory:
                with self.lock:
                    self.files_to_process.append(event.src_path)
                if self.timer is not None:
                    self.timer.cancel()
                self.timer = Timer(self.wait_time, self.convert_and_combine)
                self.timer.start()
        except Exception as e:
            logging.error(f"Error processing file {event.src_path}: {e}")

    def convert_and_combine(self):
        try:
            with self.lock:
                files = self.files_to_process.copy()
                self.files_to_process.clear()

            for file_path in files:
                logging.info(f"Adding new file: {file_path}")
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    logging.info(f"Converting: {file_path}")
                    pdf_path = file_path + '.pdf'
                    try:
                        with open(pdf_path, "wb") as f:
                            f.write(img2pdf.convert(file_path))
                        os.remove(file_path)
                        logging.info(f"Converted and removed original image: {file_path}")
                    except Exception as e:
                        logging.error(f"Failed to convert '{file_path}' to PDF: {e}")

            self.combine_pdfs()
        except Exception as e:
            logging.error(f"Error during conversion and combining: {e}")

    def combine_pdfs(self):
        try:
            output_path = os.path.join(COMBINE_WATCHER_DIRECTORIES["output"], "Combined.pdf")
            pdf_files = [
                os.path.join(COMBINE_WATCHER_DIRECTORIES["to_watch"], f)
                for f in sorted(os.listdir(COMBINE_WATCHER_DIRECTORIES["to_watch"]))
                if f.endswith('.pdf')
            ]
            logging.info(f"Combining files: {', '.join(pdf_files)}")

            if pdf_files:
                command = ['pdftk'] + pdf_files + ['cat', 'output', output_path]
                result = subprocess.call(command)
                if result != 0:
                    logging.error(f"pdftk failed with exit code {result} while combining PDFs.")
                    return

                for pdf in pdf_files:
                    dst_path = os.path.join(COMBINE_WATCHER_DIRECTORIES["done"], os.path.basename(pdf))
                    try:
                        if os.path.exists(dst_path):
                            os.remove(dst_path)
                        shutil.move(pdf, dst_path)
                        logging.info(f"Moved combined PDF to done: {pdf}")
                    except Exception as e:
                        logging.error(f"Failed to move '{pdf}' to done directory: {e}")
        except Exception as e:
            logging.error(f"Error during PDF combining: {e}")

# ================================
# Signal Handling
# ================================

def handle_signals(watchers):
    """
    Sets up signal handlers for graceful shutdown.

    Args:
        watchers (list): List of watcher instances to stop on signal.
    """
    def signal_handler(signum, frame):
        logging.info(f"Received signal {signum}. Shutting down watchers gracefully...")
        for watcher in watchers:
            watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

# ================================
# Running the Watchers
# ================================

def run_watchers():
    w = Watcher()
    cw = CombineWatcher()
    handle_signals([w, cw])  # Register signal handlers

    watcher_thread = threading.Thread(target=w.run)
    combine_watcher_thread = threading.Thread(target=cw.run)

    watcher_thread.start()
    combine_watcher_thread.start()

    watcher_thread.join()
    combine_watcher_thread.join()

# ================================
# Main Execution
# ================================

if __name__ == '__main__':
    logging.basicConfig(
        filename='/app/data/ocr.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s',
        force=True
    )
    logging.info("* Starting server *")
    run_watchers()
