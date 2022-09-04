from flask import Flask, request, render_template

from confluent_kafka import Producer

import json

def acked(err, msg):
    """Delivery report callback called (from flush()) on successful or failed delivery of the message."""
    if err is not None:
        print("failed to deliver message: {}".format(err.str()))
    else:
        print("produced to: {} [{}] @ {}".format(msg.topic(), msg.partition(), msg.offset()))

app = Flask(__name__)

@app.route('/makepayment', methods=['POST'])
def makepayment():
   payment = json.dumps(request.json['payload'])
   p = Producer(request.json['cluster'])
   p.produce('payments', value=payment, callback=acked)
   p.flush(1)
   return payment

@app.route('/')
def paymentsapp():
   return render_template("payments.html")

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5005, debug = True)
