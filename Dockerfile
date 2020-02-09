FROM python:3.7-stretch

WORKDIR /flatbot

RUN apt-get update && apt-get install -y build-essential

ADD src/flatbot /flatbot/src/flatbot
COPY requirements.txt /flatbot/requirements.txt
COPY setup.py /flatbot/setup.py
RUN pip install -r requirements.txt

ADD scripts /flatbot/scripts
ADD ssl /flatbot/ssl

COPY config.yml /flatbot/config.yml

CMD ["bash", "/flatbot/scripts/run_server.sh"]