from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider

from cassandra.cluster import ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import WhiteListRoundRobinPolicy
from cassandra.query import tuple_factory
import pika
import os
import re
import platform
import json

##
## Configure test vs. production
##
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
cassandraHost = os.getenv("CASSANDRA_HOST") or "localhost"


print("Connecting to rabbitmq({})".format(rabbitMQHost))
print("Connecting to cassandra ({})".format(cassandraHost))


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


cluster = Cluster([cassandraHost])

def insert_prices(prices_data):
  try:
    session = cluster.connect('products')

    enqueueDataToLogsExchange("Connected to cluster products","debug")

    for website in prices_data:
      for data in range(0,len(prices_data[website])):
        prices_arr = re.findall(r'\d*\.?\d+', prices_data[website][data]['productprice'])

        if len(prices_arr)>0:
          prices_data[website][data]['productprice'] = prices_arr[0]
          rows = session.execute("INSERT INTO products.products (uid,productName,productPrice,website,productimageurl,producturl,dateAdded) VALUES (uuid(),'"+ prices_data[website][data]['productname'] + "'," + str(prices_arr[0]) + ",'" + website + "','" + prices_data[website][data]['product_image_url'] + "','" + prices_data[website][data]['product_url'] + "',toTimestamp(now()));")
    
    amazonlist = sorted(prices_data['amazon'], key=lambda d: float(d['productprice'])) 
    ebaylist = sorted(prices_data['ebay'], key=lambda d: float(d['productprice']))
    bestbuylist = sorted(prices_data['bestbuy'], key=lambda d: float(d['productprice'])) 

    prices_data['amazon'] = amazonlist
    prices_data['ebay'] = ebaylist
    prices_data['bestbuy'] = bestbuylist


  except Exception as e:
    enqueueDataToLogsExchange("Exception occured" + str(e),"debug")
    print("Exception occured" + str(e))

  return prices_data


def presentindatabase(search_term):
  try:
    results = {}
    session = cluster.connect('products')
    
    rows = session.execute("SELECT * FROM products.products;")
    if(rows):
      for i in rows:
        if search_term.lower() in i[2].lower():
          if(i[4] in results):
            results[i[4]].append({
              "productname": i[2],
              "productprice": i[3],
              "website":i[4],
              "product_url":i[5],
              "product_image_url":i[6]
            })

          else:
            results[i[4]] = []
            results[i[4]].append({
              "productname": i[2],
              "productprice": i[3],
              "website":i[4],
              "product_url":i[5],
              "product_image_url":i[6]
            })
      
    
  except Exception as e:
    enqueueDataToLogsExchange("Exception occured" + str(e),"debug")
    print("Exception occured" + str(e))

  return results


def addSearchProduct(product_name):
  try:
    session = cluster.connect('products')

    rows = session.execute("INSERT INTO products.searchentries (uid,searchText,dateAdded) VALUES (uuid(),'"+ product_name + "',toTimestamp(now()));")
    print("Added records successfully")

  except Exception as e:
    enqueueDataToLogsExchange("Exception occured while adding search entries" + str(e),"debug")
    print("Exception occured" + str(e))



def getMostSearchedProducts():
  try:
    productsDict = {}
    session = cluster.connect('products')
    rows = session.execute("select * from products.searchentries;")

    if rows:
      for i in rows:
        if(i[2] in productsDict):
          productsDict[i[2]] = productsDict[i[2]] + 1
        else:
          productsDict[i[2]] = 1

    productsDict = dict(sorted(productsDict.items(), key=lambda item: item[1],reverse = True))

  except Exception as e:
    enqueueDataToLogsExchange("Exception occured while adding search entries" + str(e),"debug")
    print("Exception occured" + str(e))

  return productsDict