FROM python:3.10

WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

RUN sed -i 's/\r$//' /opt/app/docker-entrypoint.sh
RUN chmod +x /opt/app/docker-entrypoint.sh
CMD ["/opt/app/docker-entrypoint.sh"]