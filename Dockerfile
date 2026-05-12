FROM python:3.12-slim

WORKDIR /app

# OS deps minimal
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps zuerst (besseres Layer-Caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App + Daten (Destatis Tabellen 23211-0001 + 23211-0002, Jahre 1980-2024)
COPY app.py .
COPY data/ ./data/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8080/health || exit 1

# 2 Worker reichen fuer ein paar dutzend parallele Nutzer.
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "--access-logfile", "-"]
