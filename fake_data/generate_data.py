from faker import Faker
import psutil
import datetime

fake = Faker()

# I'm using epoch time here because it's easier for using it with Thanos later.
def faking_kiosk_data():
    kiosk_data = {
        # creating 10,000 data points for cpu_usage and memory_usage
        'cpu_usage': [fake.random_int(0, 100) for _ in range(10000)],
        'memory_ysage': [fake.random_int(0, 100) for _ in range(10000)],
        'memory_percnent': psutil.virtual_memory().percent,
        'timestamp': datetime.datetime.now().timestamp()
    }
    return kiosk_data