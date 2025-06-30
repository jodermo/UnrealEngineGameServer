FROM python:3.11-slim

WORKDIR /app

COPY ./DjangoBackend /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
