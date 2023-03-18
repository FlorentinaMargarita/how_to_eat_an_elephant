setup_project: install run_app

run_app:
	python3 flask_app.py

install:
	pip install -r requirements.txt

update_requirements:
	pip freeze > requirements.txt

nats_image:
	docker run -p 4222:4222 -ti nats:latest