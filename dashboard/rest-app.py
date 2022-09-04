from flask import Flask, request, render_template

from confluent_kafka import Consumer

import json
import sys

def consume_loop(consumer, topics):
    try:
        accounts = []
        consumer.subscribe(topics)

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: return accounts

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                sys.stdout.write('%% %s [%d] reached end at offset %d : %s %s\n' %
                                     (msg.topic(), msg.partition(), msg.offset(), msg.key(), msg.value()))
                
                value = json.loads(msg.value())
                field = {"ACCOUNT_ID" : msg.key().decode("utf-8").replace('"', '')}
                value.update(field)
                print(value)
                accounts.append(value)
    except:
        return []
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

app = Flask(__name__)

@app.route('/getaccountbalance', methods=['GET'])
def getaccountbalance():
   c1 = Consumer({
    'bootstrap.servers': '<instructor-cluster-1-bootstrap>:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '<ccloud-api-key>',
    'sasl.password': '<ccloud-api-secret>',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'group.id': 'dashboard-consumer'
   })

   c2 = Consumer({
    'bootstrap.servers': '<instructor-cluster-2-bootstrap>:9092',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '<ccloud-api-key>',
    'sasl.password': '<ccloud-api-secret>',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,
    'group.id': 'dashboard-consumer'
   })

   # add more consumers if using more than 2 instructor clusters

   accounts = consume_loop(c1, ['^account_balance.*']) + consume_loop(c2, ['^account_balance.*'])
   
   return json.dumps(accounts)

@app.route('/')
def dashboardapp():
   return render_template("dashboard.html")

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5007, debug = True)

