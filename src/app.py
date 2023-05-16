from nats.aio.client import Client as NATS
import asyncio
from flask import Flask
from generate_data import faking_kiosk_data
import json
from sqlalchemy import text
import json
from models import Metrics, db
from prometheus_client import push_to_gateway, Gauge
from prometheus_client.core import CollectorRegistry
import asyncio
from concurrent.futures import ThreadPoolExecutor


nats_url = "nats://nats:4222"
# nats_url = os.environ.get('NATS_URL')


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
    cpu_usage_gauge = Gauge(f'kiosk_cpu_usage', 'CPU usage of the kiosk at index', ['kiosk_number', 'id'], registry=registry)
    memory_usage_gauge = Gauge(f'kiosk_memory_usage', f'Memory usage of the kiosk at index', ['kiosk_number', 'id'], registry=registry)
    memory_percent_gauge = Gauge('kiosk_memory_percent', 'Memory percentage usage of the kiosk', [ 'kiosk_number', 'id'], registry=registry)

    async def run():
        nc = NATS()
        await nc.connect(nats_url)
        
        async def message_handler(msg):
            subject = msg.subject
            data = msg.data.decode()
            print('DO YOU EVEN GET HERE?')
            kiosk_number = 0
            if msg.subject == "kiosk_data_1": 
                kiosk_number = 1
            else:
                kiosk_number = 2

            print(msg.subject, 'msg.subject in se aweseome message safer')
            print(kiosk_number, 'kiosk_number')
            print(data, 'data')


            with app.app_context():
                db.session.commit()
                data_dict = json.loads(data.replace("'", "\""))
                metric = Metrics(
                id=data_dict['id'],
                kiosk_nr= kiosk_number,
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
                    stmt = text('SELECT create_hypertable(:table_name, :partition_column, migrate_data => true)')
                    db.session.execute(stmt, {'table_name': 'metrics', 'partition_column': 'timestamp'})
                    db.session.commit()  
                print(f"Received message on subject '{subject}'")
                handle_prometheus_stuff(data_dict, kiosk_number)
            
        
        def handle_prometheus_stuff(data_dict, kiosk_number):
            print('inside of handle_prometheus_stuff')
            kiosk_number = f'kiosk_number_{kiosk_number}'
            print(data_dict['cpu_usage'][0], 'data_dict[cpu_usage][0]')
            with app.app_context():
                for i in range(len(data_dict['cpu_usage'])):
                    id= f'{data_dict["id"]} metric nr {i}'
                    cpu_usage_gauge.labels( kiosk_number=kiosk_number, id=id).set(data_dict['cpu_usage'][i])

                for i in range(len(data_dict['memory_usage'])):
                    id= f'{data_dict["id"]} metric nr {i}'
                    memory_usage_gauge.labels( kiosk_number=kiosk_number, id=id).set(data_dict['cpu_usage'][i])
                

                memory_percent_gauge.labels( kiosk_number=kiosk_number, id=data_dict['id']).set(data_dict['memory_percent'])
        
        await nc.subscribe("kiosk_data_1", cb=message_handler)
        await nc.subscribe("kiosk_data_2", cb=message_handler)



        async def publish_metrics():
            # method runs concurrently on two cores of the machine 
            # loop = asyncio.get_running_loop()
            with ThreadPoolExecutor(max_workers=2) as executor:
                kiosk_data_1 = loop.run_in_executor(executor, faking_kiosk_data)
                kiosk_data_2 = loop.run_in_executor(executor, faking_kiosk_data)
                results = await asyncio.gather(kiosk_data_1, kiosk_data_2)
            await nc.publish("kiosk_data_1", str(results[0]).encode())
            await nc.publish("kiosk_data_2", str(results[1]).encode())
            push_to_gateway("http://pushgateway:9091", job='kiosk_data', registry=registry)

        
        async def publish_metrics_periodically():
            while True:
                await publish_metrics()
                await asyncio.sleep(1)
        

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