from nats.aio.client import Client as NATS
import asyncio
from flask import Flask, Response
from generate_data import faking_kiosk_data
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
import json
from flask_sqlalchemy import SQLAlchemy
from models import Metrics, db
from prometheus_client import Histogram, generate_latest, push_to_gateway, Counter, Gauge
from prometheus_client.core import CollectorRegistry
from prometheus_flask_exporter import PrometheusMetrics
import asyncio

# prometheus_histogram = Histogram("nats_message_latency_seconds", "Latency of NATS message processing")

nats_url = "nats://nats:4222"
# nats_url = os.environ.get('NATS_URL')


registry = CollectorRegistry()
prometheus_counter = Counter("nats_message_count", "Total number of NATS messages received", registry=registry)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://elephant:onebiteatatime@timescaledb:5432/elephantdatabase'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.session.execute(text('CREATE EXTENSION IF NOT EXISTS timescaledb;'))        
        db.create_all()
        db.session.commit() 

    print('finit!')
    registry = CollectorRegistry()
    n=10
    cpu_usage_gauge = [Gauge(f'kiosk_cpu_usage_{i}', f'CPU usage of the kiosk at index {i}', ['id'], registry=registry) for i in range(n)]
    memory_usage_gauge = [Gauge(f'kiosk_memory_usage_{i}', f'Memory usage of the kiosk at index {i}', ['id'], registry=registry) for i in range(n)]
    # cpu_usage_gauge = Gauge('kiosk_cpu_usage', 'CPU usage of the kiosk', ['cpu_usage'], registry=registry)
    # memory_usage_gauge = Gauge('kiosk_memory_usage', 'Memory usage of the kiosk', ['memory_usage'], registry=registry)
    memory_percent_gauge = Gauge('kiosk_memory_percent', 'Memory percentage usage of the kiosk', ['memory_percent'], registry=registry)
    print(memory_percent_gauge, 'memory_percent_gauge up top')

    @app.route('/metrics', methods=['GET'])
    def metrics():
        return Response(generate_latest(registry), content_type='text/plain')
    
    @app.route('/health', methods=['GET'])
    def health():
        return 'I am healthy'

    async def run():
        nc = NATS()
        await nc.connect(nats_url)

        async def publish_metrics():
            kiosk_data = faking_kiosk_data()
            await nc.publish("kiosk_data", str(kiosk_data).encode())

            return "publishing stuff"
        
        
        async def message_handler(msg):
            subject = msg.subject
            data = msg.data.decode()
            print(data, 'data in se aweseome message safer')

            with app.app_context():
                db.session.commit()
                data_dict = json.loads(data.replace("'", "\""))
                metric = Metrics(
                id=data_dict['id'],
                     
                cpu_usage=data_dict['cpu_usage'],
                memory_usage=data_dict['memory_usage'],
                memory_percent=data_dict['memory_percent'],
                timestamp=data_dict['timestamp']
            )
                db.session.add(metric)
                db.session.commit()

                db.session.execute(text('CREATE EXTENSION IF NOT EXISTS timescaledb;'))        
                db.create_all()
                db.session.commit()

                stmt = text('SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename = :table_name AND tableowner = CURRENT_USER)')
                result = db.session.execute(stmt, {'table_name': 'metrics'}).fetchone()[0]
                if result:
                    print(f"Hypertable {'metrics'} already exists.")
                else:
                    print("IN THE ELSE")
                    stmt = text('SELECT create_hypertable(:table_name, :partition_column, migrate_data => true)')
                    db.session.execute(stmt, {'table_name': 'metrics', 'partition_column': 'timestamp'})
                    db.session.commit()  
                print(f"Received message on subject '{subject}': {data}")

                print('on top of prometheus nats stuff')
                handle_prometheus_stuff(data_dict)
            
        
        def  handle_prometheus_stuff(data_dict):
            print('inside of handle_prometheus_stuff')

            with app.app_context():
                for i, cpu_usage in enumerate(data_dict['cpu_usage']):
                    cpu_usage_gauge[i].labels(id=data_dict['id']).set(cpu_usage)
    
                for i, memory_usage in enumerate(data_dict['memory_usage']):
                    memory_usage_gauge[i].labels(id=data_dict['id']).set(memory_usage)
                memory_percent_gauge.labels(memory_percent=data_dict['memory_percent']).set(data_dict['memory_percent'])
                        
           
        await nc.subscribe("kiosk_data", cb=message_handler)

        print(prometheus_counter, 'prometheus_counter')
        print(registry, 'registry')

        async def publish_metrics():
            kiosk_data = faking_kiosk_data()
            await nc.publish("kiosk_data", str(kiosk_data).encode())
            push_to_gateway("http://pushgateway:9091", job='kiosk_data', registry=registry)
            # return Response(generate_latest(registry), content_type='text/plain')

        
        async def publish_metrics_periodically():
            while True:
                await publish_metrics()
                await asyncio.sleep(1)  # 1 second interval
        

        asyncio.create_task(publish_metrics_periodically())

        while True:
            await asyncio.sleep(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.close()
    return app
    

if __name__ == '__main__':
        app = create_app()
        app.run(host='0.0.0.0', port=5000)