setup_project: install run_app

run_app:
	python3 src/app.py

run_app_in_docker:
	docker-compose up

install:
	pip install -r requirements.txt

update_requirements:
	pip freeze > requirements.txt

nats_image:
	docker run -p 4222:4222 -ti nats:latest

prometheus_exporter_image:
	docker build -t prometheus-nats-exporter .
	docker run -p 7777:7777 prometheus-nats-exporter

prune_images:
	docker image prune -a

# delete_docker_stuff:
# 	docker stop $(docker ps -aq)
# 	docker rm -f $(docker ps -aq)
# 	docker rmi -f $(docker images -a -q)

prune_docker:
	docker system prune

interact_with_database:
	docker exec -it aba181ac8945 psql -U elephant elephantdatabase

port_500_check:
	sudo lsof -i :5000

