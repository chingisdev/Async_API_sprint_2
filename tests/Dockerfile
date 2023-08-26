FROM python:3.11

WORKDIR /app/tests

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

RUN sed -i 's/\r$//' entrypoint.sh
RUN chmod +x entrypoint.sh

CMD ["/app/tests/entrypoint.sh"]

