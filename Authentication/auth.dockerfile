FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY source ./source
COPY migrations ./migrations

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]