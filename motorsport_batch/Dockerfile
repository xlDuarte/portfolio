FROM python:3.11-slim
WORKDIR /app
COPY requirements-motorsport-mlops.txt ./
RUN pip install --no-cache-dir -r requirements-motorsport-mlops.txt
COPY motorsport_batch ./motorsport_batch
RUN useradd -r -u 10001 appuser && mkdir -p /artifacts && chown -R appuser:appuser /artifacts
USER appuser
EXPOSE 8000
CMD ["uvicorn","motorsport_batch.service:app","--host","0.0.0.0","--port","8000"]
