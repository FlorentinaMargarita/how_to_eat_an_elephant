# How to run the app in Docker

In the terminal just run `docker-compose up`. 

* Grafana: `http://localhost:3000/` both username and password are `admin`.
* Thanos-Quierer UI out of the box: http://localhost:19192/
* Prometheus out of the box UI: http://localhost:9090/

This project is designed to run on MacOS. If you are using Windows, I recommend using the Windows Subsystem for Linux (WSL), specifically with Ubuntu.
FAQ: 
Q: What do I do when I get a permission denied error for the script `wait-for.sh`?
A: Just run `sudo chmod +x ./wait-for.sh`, put in your password and it should work fine.