FROM python:3.10.6-slim-buster

WORKDIR /app

COPY requ.txt .
COPY src .


RUN python3 -m pip install -r requ.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]