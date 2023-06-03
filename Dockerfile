FROM python:3.10.6-slim-buster

WORKDIR /app
RUN apt-get update && apt-get install -y netcat
RUN apt-get update && apt-get install -y python3-pip
RUN pip install prometheus_client
RUN pip install prometheus-flask-exporter 

COPY requ.txt .
COPY wait-for.sh .
RUN chmod +x ./wait-for.sh
COPY src .
RUN python3 -m pip install -r requ.txt

COPY . .


CMD ["./wait-for.sh", "timescaledb", "5432", "python", "app.py"]