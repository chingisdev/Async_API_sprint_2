FROM python:3.11

WORKDIR /app

ENV UVICORN_WORKERS_NUM 16

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

EXPOSE 8000
RUN sed -i 's/\r$//' /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh
CMD ["/app/docker-entrypoint.sh"]
