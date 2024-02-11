import os
import time
import shutil
import img2pdf
import subprocess
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CombineWatcher:
    DIRECTORY_TO_WATCH = "/app/data/combine"
    DIRECTORY_OUTPUT = "/app/data/input"  # Save combined pdf to the OCR input folder 
    DIRECTORY_DONE = "/app/data/done"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = CombineHandler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class CombineHandler(FileSystemEventHandler):
    def __init__(self):
        self.timer = None
        self.wait_time = 5  # Waiting time for more files in seconds
        self.files_to_process = []  # List for storing file paths to be processed
    
    def on_created(self, event):
        if not event.is_directory:
            self.files_to_process.append(event.src_path)  # Add file path to the list
            # Reset the timer every time a new file is added
            if self.timer is not None:
                self.timer.cancel()
            self.timer = Timer(self.wait_time, self.convert_and_combine)
            self.timer.start()
    
    def convert_and_combine(self):
        for file_path in self.files_to_process:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                pdf_path = file_path + '.pdf'
                # Convert image to PDF
                with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(file_path))
                # Delete the original image file
                os.remove(file_path)
        
        # Clear the list after processing
        self.files_to_process.clear()
        
        # Combine all PDF files in the directory after converting all new images
        self.combine_pdfs(CombineWatcher.DIRECTORY_TO_WATCH, CombineWatcher.DIRECTORY_OUTPUT, CombineWatcher.DIRECTORY_DONE)

    def combine_pdfs(self, input_dir, output_dir, done_dir):
        output_path = os.path.join(output_dir, "combined.pdf")
        pdf_files = [os.path.join(input_dir, f) for f in sorted(os.listdir(input_dir)) if f.endswith('.pdf')]
        if pdf_files:
            command = ['pdftk'] + pdf_files + ['cat', 'output', output_path]
            subprocess.call(command)

        # Move combined files to the done directory, overwrite if exists
        for pdf in pdf_files:
            src_path = pdf
            dst_path = os.path.join(done_dir, os.path.basename(pdf))
            if os.path.exists(dst_path):
                os.remove(dst_path)  # Delete existing file before moving
            shutil.move(src_path, dst_path)

if __name__ == "__main__":
    watcher = CombineWatcher()
    watcher.run()
