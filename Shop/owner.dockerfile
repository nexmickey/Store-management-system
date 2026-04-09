FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY source_common ./source_common
COPY source_owner ./source_owner
COPY solidity ./solidity
COPY migrations ./migrations

ENV PYTHONPATH="/app"

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]