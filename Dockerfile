FROM python:3.7-stretch

RUN apt-get update && apt-get install -y build-essential

WORKDIR /flatbot

COPY src/flatbot src/flatbot
COPY requirements/production.txt requirements.txt
COPY setup.py setup.py
RUN pip install -r requirements.txt

COPY scripts scripts
COPY ssl ssl
COPY .env config.yml
COPY cred.json cred.json