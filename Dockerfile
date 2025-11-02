FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y openssl && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
