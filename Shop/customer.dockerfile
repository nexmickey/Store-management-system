FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY source_common ./source_common
COPY source_customer ./source_customer
COPY solidity ./solidity

ENV PYTHONPATH="/app"

ENTRYPOINT [ "python", "./source_customer/main.py" ]