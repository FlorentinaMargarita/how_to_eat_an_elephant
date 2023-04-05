FROM python:3.10.6-slim-buster

WORKDIR /app

COPY requ.txt .
COPY src .
COPY prometheus_edit.yml .

RUN python3 -m pip install -r requ.txt

COPY . .


CMD ["python", "app.py"]