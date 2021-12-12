FROM python:3.8

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install --upgrade pika redis jsonpickle requests flask uuid Flask-Cors cassandra-driver
COPY  . /home/

ENV PYTHONPATH "${PYTHONPATH}:/home"

WORKDIR /home

EXPOSE 5000

CMD	[ "python3", "server.py" ]