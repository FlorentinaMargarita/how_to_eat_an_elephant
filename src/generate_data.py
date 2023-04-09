from faker import Faker
import psutil
import datetime

fake = Faker()

def faking_kiosk_data():
    kiosk_data = {
        # creating data points for cpu_usage and memory_usage
        "id": fake.pystr_format(),
        "cpu_usage": [fake.random_int(0, 100) for _ in range(1000)],
        "memory_usage": [fake.random_int(0, 100) for _ in range(1000)],
        "memory_percent": psutil.virtual_memory().percent,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }
    return kiosk_data