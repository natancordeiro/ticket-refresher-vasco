FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-common \
    fonts-liberation \
    libglib2.0-0 libnss3 libgdk-pixbuf-2.0-0 libgtk-3-0 \
    libasound2 libxdamage1 libxrandr2 libxcomposite1 libxss1 libxfixes3 libxi6 libxtst6 \
    libdrm2 libgbm1 libxshmfence1 libu2f-udev \
    ca-certificates wget \
    fonts-noto fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash app
WORKDIR /app

RUN mkdir -p /data/profile /data/screenshots /data/downloads /app/logs /app/runs && \
    chown -R app:app /data /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER app

ENV HEADLESS=true \
    USER_DATA_DIR=/data/profile \
    SCREENSHOT_DIR=/data/screenshots \
    DOWNLOAD_DIR=/data/downloads \
    LOG_LEVEL=INFO \
    TZ=America/Sao_Paulo

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-u", "main.py"]
