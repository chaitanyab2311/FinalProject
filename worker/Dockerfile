FROM python:3.8

ADD worker-server.py /

RUN pip3 install --upgrade pika redis jsonpickle requests beautifulsoup4 cassandra-driver

COPY . /root/scraper_worker

CMD cd /root/scraper_worker && \
    python3 worker-server.py