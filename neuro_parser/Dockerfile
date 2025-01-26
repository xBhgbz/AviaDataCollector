FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr \
    flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-rus && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install 'pip<24.0' textract && mkdir -p /app/src/files

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]
