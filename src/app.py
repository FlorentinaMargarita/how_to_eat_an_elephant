from nats.aio.client import Client as NATS
import asyncio
from flask import Flask, jsonify
import multiprocessing

from generate_data import faking_kiosk_data
# from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

nats_url = "nats://localhost:4222"  

async def connect_nats():
    nc = NATS()
    await nc.connect(nats_url)
    return nc


# with asyncio library connection to NATS is asynchronously, which is recommended for using NATS in prod.
nc = asyncio.run(connect_nats())

@app.before_first_request
def init():
    nc

@app.route('/')
def healthz():
    return 'How do you eat an elephant? One bite at a time.'


@app.route('/publish_metrics')
def publish_metrics():
    kiosk_data = faking_kiosk_data()
    nc.publish("kiosk_data", str(kiosk_data).encode())

    return "publishing stuff"

def emit_data(q):
    print('below emit_data')

    with app.app_context():
        while True:
            data = faking_kiosk_data()
            q.put(data)

if __name__ == '__main__':
    q = multiprocessing.Queue()
    # target means which function should be run by the process
    p1 = multiprocessing.Process(target=emit_data, args=(q,))
    p2 = multiprocessing.Process(target=emit_data, args=(q,))
    p1.start()
    p2.start()
    app.run()
