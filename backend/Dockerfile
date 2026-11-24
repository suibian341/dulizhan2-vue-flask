FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend
COPY frontend/src/messages /app/frontend/src/messages

RUN mkdir -p /app/backend/uploads

EXPOSE 5000

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
