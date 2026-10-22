FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ADVANCED_DB_PATH=/data/events.sqlite3
COPY requirements-advanced.txt ./
RUN pip install --no-cache-dir -r requirements-advanced.txt
COPY advanced_batch ./advanced_batch
RUN mkdir -p /data && useradd -r -u 10001 appuser && chown -R appuser:appuser /data /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=4)"
CMD ["uvicorn","advanced_batch.api:app","--host","0.0.0.0","--port","8000"]
