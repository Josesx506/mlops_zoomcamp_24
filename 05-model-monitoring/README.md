### Environment Setup
Install virtual environment with pipenv `pipenv install numpy==1.26.4 flask --python=3.12`. Additional environment packages are in the `requirements.txt` and `Pipfile` files. <br>

Create a docker-compose setup for grafana. The compose file should have central mounted volume for storing data.
- Create a `config` directory for storing the grafana configuration yaml files. This allows a configuration of the postresql db to point to grafana dashboard. The environment is run locally and all services are free but you have to uses `http://localhost/<app_port>` to access the correct service like grafana.
- Default grafana username and password is `admin` and `admin`, following which you are prompted to set a new password.