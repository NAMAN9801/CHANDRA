FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV APP_HOST=0.0.0.0
ENV APP_PORT=5000
ENV MAX_CONTENT_LENGTH_MB=16
ENV OUTPUT_DIR=/app/uploads
ENV GUNICORN_WORKERS=2
ENV GUNICORN_TIMEOUT=120

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p "${OUTPUT_DIR}"

EXPOSE 5000

CMD ["/bin/sh", "-c", "gunicorn --bind ${APP_HOST}:${APP_PORT} --workers ${GUNICORN_WORKERS} --timeout ${GUNICORN_TIMEOUT} app:app"]
