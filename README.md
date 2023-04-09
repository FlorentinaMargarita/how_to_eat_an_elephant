# How to run the app in Docker

In the terminal just run `docker-compose up`. 
Go to localhost... 

* If you open grafana on `http://localhost:3000/` both username and password are `admin`.

Thanos-Quierer UI: http://localhost:19192/

# How to run the application locally

Open 2 terminals: 
1. In the first terminal run `make nats_image`
2. In the second terminal run `make setup_project` or follow the corresponding rules in the Makefile.