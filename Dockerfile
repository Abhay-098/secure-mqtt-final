FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y openssl && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# 💥 CRITICAL FIX: Use Gunicorn with Eventlet worker
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "app:socketio"]
