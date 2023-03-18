from flask import Flask
from nats.aio.client import Client as NATS
import asyncio
import random


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
def hello():
    return 'Hello, World!'


@app.route('/metrics')
def metrics():
    # Generate fake metrics
    cpu_usage = random.uniform(0, 100)
    mem_usage = random.uniform(0, 100)
    disk_usage = random.uniform(0, 100)

    # Publish metrics on NATS
    nc.publish("fake-metrics.cpu_usage", str(cpu_usage).encode())
    nc.publish("fake-metrics.mem_usage", str(mem_usage).encode())
    nc.publish("fake-metrics.disk_usage", str(disk_usage).encode())

    return "OK"

if __name__ == '__main__':
    # asyncio.run(metrics())
    app.run()
