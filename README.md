
# Description
OCR-Machine is a container for text detection in PDF files using OCRMyPDF and Tesseract-OCR.
It can be run as a standalone Docker image and is also supported on Kubernetes.
The Docker image includes all languages supported by Tesseract. Please set the appropriate language in the configuration file.

## Features:
- Apply OCR using AI
- Convert PNG and JPG to PDF
- Merge multiple files into a single PDF
- Extract text into a TXT file

## Requirements
- 3GB HDD
- 3GB RAM

# Usage
After starting, the application will automatically create required directories and a log file in the home folder.
The config.txt must be created manually.

### OCR
1. Upload PDF files to the input directory.
2. Wait for the program to process the files.
3. Original files will be moved to the done or error directories in case of success or a processing problem.
4. Processed files will be saved in the output directory, accompanied by a .txt file containing the extracted text for each document.

### Convert and Combine
1. Upload one or multiple PDF,PNG,JPG files to the combine directory.
2. JPG and PNG files will be automatically converted to PDF.
3. All PDF files will be merged in alphabetical order into a single file named Combined.pdf.
4. The Combined.pdf file will then be automatically moved to the Input folder and processed using OCR.
5. The final file will be saved in the Output folder.

# Installation in Docker container
```
# Clone the repository
# (optional) docker build -t ocr-machine .
docker compose up -d
```
# Installation in Kubernetes
Prepare a persistent volume for the container for example: //fileserver/OCR
#### YAML configuration

Password for the Secret
```
echo -n 'password' | base64
```
smb-secret.yaml
```
apiVersion: v1
kind: Secret
metadata:
  name: smb-secret
  namespace: default
type: Opaque
data:
  username: ******
  password: ******
```
ocr-pv.yaml
```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ocr-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  csi:
    driver: smb.csi.k8s.io
    volumeHandle: samba-volume
    volumeAttributes:
      source: "//fileserver/OCR"
    nodeStageSecretRef:
      name: smb-secret
      namespace: default
```
ocr-pvc.yaml
```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ocr-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  volumeName: ocr-pv
```
ocr-deployment-pvc.yaml
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ocr-machine
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ocr-app
  template:
    metadata:
      labels:
        app: ocr-app
    spec:
      containers:
      - name: ocr-container
        image: huculski/ocr-machine:latest
        command: ["python3", "ocr.py"]
        volumeMounts:
        - name: ocr-storage
          mountPath: /app/data
      volumes:
      - name: ocr-storage
        persistentVolumeClaim:
          claimName: ocr-pvc
```
#### Start Pods
```
kubectl apply -f smb-secret.yaml
kubectl apply -f ocr-pv.yaml
kubectl apply -f ocr-pvc.yaml  
kubectl apply -f ocr-deployment-pvc.yaml
```

# Configuration
Create a configuraion file: ~/ocr/config.txt
The configuration is automatically loaded at the start of each OCR processing. There is no need to restart the container to apply changes to the file.
```
# Number of documents being processed at the same time
max_workers = 2

# Language of the file to be OCRed (see https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html for supported language packs).
language = pol

# For input image instead of PDF, use this DPI instead of file's.
image_dpi = 300

# Control  how  PDF  is optimized after processing:
# 0 - do not optimize; 1 - do safe, lossless optimizations (default); 2 - do some lossy optimizations; 3 - do aggressive
optimize = 1

# Set Tesseract OCR engine mode: 0 - original Tesseract only; 1 - neural nets LSTM only; 2 - Tesseract + LSTM; 3 - default.
tesseract-oem = 2
```

# docker-compose.yml
```
services:
  ocr-machine:
    image: huculski/ocr-machine:latest
    container_name: ocr-machine
    restart: unless-stopped
    volumes:
      - ./ocr:/app/data
```
