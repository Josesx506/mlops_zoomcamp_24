### Orchestration
Create a virtual docker environment with the docker compose file. Change the directory to this folder `03-model-deployment` and launch the server with `./scripts/start.sh`.
- The `settings.yaml` and `requirements.txt` must be present to install environment packages and make sure that mage recognizes the project as a *multi-project* environment.
- In the `docker-compose.yaml` file, the postgres server, mage server, and mlflow server are sharing the same network `app-network`
- Once the server is launched, click on 
    - `http://localhost:6789` to access the ***MAGE UI*** server
    - `http://localhost:3500` to acess the ***MLFlow UI*** server