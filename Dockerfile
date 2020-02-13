FROM python:3.7-stretch

RUN apt-get update && apt-get install -y build-essential

WORKDIR /flatbot

COPY src/flatbot src/flatbot
COPY requirements/production.txt requirements.txt
COPY setup.py setup.py
RUN pip3 install -r requirements.txt

COPY scripts scripts

CMD flatbot-run