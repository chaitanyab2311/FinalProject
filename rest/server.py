##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import json
import pickle
import uuid
from flask_cors import CORS
import sys
sys.path.insert(0, '')
import db



class enqueueWorker(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
 
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.onResponse,
            auto_ack=True)
    
    def onResponse(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body


    def enqueueDataToWorker(self,message):

        self.response = None
        self.corr_id = str(uuid.uuid4())

    
        self.channel.basic_publish(
            exchange='', routing_key='toWorker',properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ), 
            body=json.dumps(message))


        while self.response is None:
            self.connection.process_data_events()
        
        return str(self.response.decode('utf-8'))



# Initialize the Flask application
app = Flask(__name__)
CORS(app) # This will enable CORS for all routes


##
## Configure test vs. production
##
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({})".format(rabbitMQHost))



def enqueueDataToLogsExchange(message,messageType):
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()

    rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')

    infoKey = f"{platform.node()}.rest.info"
    debugKey = f"{platform.node()}.rest.debug"

    if messageType == "info":
        key = infoKey
    elif messageType == "debug":
        key = debugKey

    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key='logs', body=json.dumps(message))

    print(" [x] Sent %r:%r" % (key, message))

    rabbitMQChannel.close()
    rabbitMQ.close()



@app.route('/apiv1/fetchPrices', methods=['POST'])
def analyze():
    try:

        # enqueueDataToLogsExchange('Into fetch prices api',"info")

        data = request.get_json()
        product = data['product_name']

        dataToWorker = enqueueWorker()
        response = dataToWorker.enqueueDataToWorker(data)

        response = json.loads(response)
        print(type(response))

        # enqueueDataToLogsExchange('Fetch prices api executed succesfully',"info")

        return Response(response=json.dumps(response), status=200, mimetype="application/json")
        
    except Exception as e:
        print("Exception" + str(e))
        enqueueDataToLogsExchange('Error occured in api /apiv1/analyze','info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")



@app.route('/apiv1/getMostSearched', methods=['POST'])
def most_searched():
    try:

        enqueueDataToLogsExchange('Into get most searched api',"info")

        most_searched = db.getMostSearchedProducts()

        enqueueDataToLogsExchange('After get most searched api',"info")

        return Response(response=json.dumps(most_searched), status=200, mimetype="application/json")

    except Exception as e:
        print("Something went wrong" + str(e))
        enqueueDataToLogsExchange('Error occured in api /apiv1/getMostSearced' + str(e),'info')
        return Response(response="Something went wrong!", status=500, mimetype="application/json")



# start flask app
app.run(host="0.0.0.0", port=5000)
