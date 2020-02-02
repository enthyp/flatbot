FROM python:3.7-stretch

WORKDIR /flatbot
ADD src/flatbot /flatbot/src/flatbot
ADD scripts /flatbot/scripts
ADD ssl /flatbot/ssl

COPY setup.py /flatbot/setup.py
COPY config.yml /flatbot/config.yml

RUN apt-get update && apt-get install -y build-essential && pip install .
CMD ["flatbot-run"]