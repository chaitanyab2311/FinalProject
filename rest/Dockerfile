FROM python:3.8

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install --upgrade pika redis jsonpickle requests flask
COPY  rest-server.py rest-server.py

EXPOSE 5000

CMD	[ "python3", "rest-server.py" ]