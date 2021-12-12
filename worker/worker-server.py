
import pickle
import platform
import io
import os
import sys
import pika
import hashlib
import json
import requests

import sys
sys.path.insert(0, '')
import db
import scrape


## Configure test vs. production
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
print(f"Connecting to rabbitmq({rabbitMQHost})")
rabbitMQChannel = None                                                
try:
    ## Set up rabbitmq connection
    rabbitMQ = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitMQHost))
    rabbitMQChannel = rabbitMQ.channel()
    toWorkerResult = rabbitMQChannel.queue_declare(queue='toWorker')

    queue_name = toWorkerResult.method.queue
except Exception as e:
    print("Exception occured " + str(e))



def callback(ch, method, properties, body):
    print(f" [x] {method.routing_key}:{body}", file=sys.stdout, flush=True)
    queuedata = json.loads(body)

    product = queuedata['product_name']

    final_output = scrape.start_scraping(product)
    response = db.insert_prices(final_output)
    db.addSearchProduct(product)

    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id = properties.correlation_id),
                     body=json.dumps(response))

    ch.basic_ack(delivery_tag=method.delivery_tag)

    sys.stdout.flush()
    sys.stderr.flush()


rabbitMQChannel.basic_qos(prefetch_count=1)
rabbitMQChannel.basic_consume(queue='toWorker', on_message_callback=callback)
rabbitMQChannel.start_consuming()