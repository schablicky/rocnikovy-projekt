FROM python:3.11.3-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV DJANGO_SETTINGS_MODULE=trading_web.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0

RUN echo '#!/bin/bash\n\
case "$1" in\n\
  "web")\n\
    cd trading_web && python manage.py migrate && python manage.py runserver 0.0.0.0:8000\n\
    ;;\n\
  "worker")\n\
    cd trading_web && celery -A trading_web worker -l INFO\n\
    ;;\n\
  "beat")\n\
    cd trading_web && celery -A trading_web beat -l INFO\n\
    ;;\n\
  "ai")\n\
    cd aitrading && python main.py\n\
    ;;\n\
  *)\n\
    exec "$@"\n\
    ;;\n\
esac' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["web"]