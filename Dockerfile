FROM python:3.7-stretch

RUN apt-get update && apt-get install -y build-essential

WORKDIR /flatbot

COPY src/flatbot src/flatbot
COPY requirements/production.txt requirements.txt
COPY setup.py setup.py
RUN pip install -r requirements.txt

COPY scripts scripts
COPY ssl ssl
COPY config.yml config.yml
COPY cred.json cred.json

ENV CONFIG_PATH /flatbot/config.yml
ENV GOOGLE_APPLICATION_CREDENTIALS /flatbot/cred.json

CMD ["bash", "/flatbot/scripts/run_server.sh"]
