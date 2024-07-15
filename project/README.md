### Project Description
Predict number of motor vehicle incidents based on `location_id | dayOfWeek | hourOfDay` in NYC. This can provide crash history alerts to drivers at the start of their journey (by modeling a preferred route between two points in this simple implementation) or dynamic alerts based on proximity to a specific location as the crow flies on their chosen routes. This project was inspired by a [Waze alert](https://blog.google/waze/crash-history-alerts-arrive-to-the-waze-map/) that I got on a recent journey.

### Setup Overview
The project has 3 major components, a backend for traininging the model, a web server for serving the predictions, and a frontend for accessing the webserver. Considering the complexity of setting up each individual component, the major components were containerized into a different docker services that share the same internal networks. <br>

The model registry saves artifacts to an s3 bucket so you'll need to configure aws-cli first. Once you have an access key, secret acccess, and default region, you can create a `.env` file and save your credentials within it like
```bash
export AWS_ACCESS_KEY=XXXXXXX
export AWS_SECRET_KEY=XXXXXX
export AWS_Zone=us-east-1
export S3_URI=s3://mlflow-artifacts-zmcp24/
```
Activate the environment in your terminal with `source .env` (for mac and linux), then launch all the services with `docker-compose up -d` from the *`repo/project`* directory. This creates 6 services simulataneously. A few of the services spin up faster than others so you might need to wait a bit. The services, entrypoints, and image sizes on a mac are shown below

| Service Name | Entrypoint | Size (GB) |
| :----------- | :--------: | :-------: |
| adminer | http://localhost:8080 | 0.25 |
| db | http://localhost:5436 | 0.43 |
| grafana | http://localhost:3000 | 0.44 |
| mlflow | http://localhost:5150 | 1.07 |
| mlserver | http://localhost:8534 | 2.83 |
| webpack | http://localhost:9300 | 0.29 |

This requires significant storage space, so you make sure your local/remote instance has a enough storage to avoid build errors. <br><br>

If you don't want s3, you can modify the `docker-compose.yaml` file, and remove the `--default-artifact-root` argument from the command step of the *mlflow service*. This can limit other steps like orchestration etc.
```bash
services:
  mlflow:
    command: mlflow server -h 0.0.0.0 -p 5150 --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=${S3_URI}
```

The container is hosted on an EC2 instance with exposed external ports 





### Data and Tools
- [x] [Maps](https://leafletjs.com/)
- [x] [Geocoding](https://smeijer.github.io/leaflet-geosearch/)
- [x] [AOI Masking](https://github.com/ptma/Leaflet.Mask/blob/master/README.md)
- [x] [Motor Vehicle Collisions](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data)



### Setting up MLFlow Server
- Install packages to launch the environment
    ```bash
    sudo apt-get update
    sudo apt install python3-pip
    sudo python3 -m pip install awscli --break-system-packages
    aws configure              # Include access key and secret
    sudo apt install pipenv
    sudo apt install --reinstall python3-pkg-resources python3-setuptools
    pipenv shell
    pipenv install scikit-learn flask mlflow setuptools --python=3.12
    ```
- Start the server
    ```bash
    mlflow server --host 0.0.0.0 -p 5100 --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=s3://mlflow-artifacts-joses/
    ```
- Set up inbound security rules to allow you access on the desired port, in this case `:5100`.
- Connect to the server using the instances public IP address. It should look something like `http://ec2-100-26-136-60.compute-1.amazonaws.com:5000`.
    > Note: `http://` should be used instead of `https://`. No **s** unless it won't connect.
- Now we're ready to start training the model.




`docker-compose up -d`

check that the postgres password in the docker-compose file matches the one in the grafana `config/grafana_datasources.yaml` file


### Setting up the environment
Run `docker-compose up -d` in detach mode from the `repo/project` directory. This will spin the services below. Forwarded ports are indicated below
- [x] Ml server                  - http://localhost:8534/
- [x] Mlflow (for Mlserver)      - http://localhost:5150/
- [x] Grafana dashboard          - http://localhost:3000/
- [x] Postgres db (for Grafana)  - http://localhost:5436/
- [x] Adminer (for sql servers)  - http://localhost:8080/

For the 5 services, only ***Adminer,Mlflow, and Grafana*** have a visible UI when you click the link. 


npm run serve

poetry export --without-hashes --format=requirements.txt > requirements.txt

docker build --no-cache --build-arg -t wbserver:v1 -f docker-files/Dockerfile.webpack .
docker run --rm -p 9300:9300 wbserver:v1



docker build --no-cache -t statserver:v1 -f docker-files/Dockerfile.appserver .
docker run --rm -p 8536:8536 statserver:v1
docker build -t statserver:v1 -f docker-files/Dockerfile.appserver .
docker run --rm -ti -t statserver:v1 bash


docker build --no-cache --build-arg AWS_ACCESS_KEY_ID=$AWS_KEY --build-arg AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY --build-arg AWS_DEFAULT_REGION=$AWS_REGION -t mlserver:v1 -f docker-files/Dockerfile.mlserver .

docker run --rm -p 8534:8534 mlserver:v1 &

<!-- poetry export --without-hashes --format=requirements.txt > requirements.txt -->
docker build -t mlserver:v1 --file Dockerfile.mlserver 


poetry export --without-hashes --format=requirements.txt > requirements.txt

### Hotfix and restart a single docker-compose service without stopping all the other containers
docker-compose up -d --no-deps --build <service_name>

docker-compose up -d --build mlflow


curl -X POST -H "Content-Type: application/json" -d '{
  "coords": {
    "start-address": {
      "lng": "-73.7793733748521",
      "lat": "40.642947899999996"
    },
    "end-address": {
      "lng": "-74.0098809",
      "lat": "40.706619"
    }
  }, 
  "cutoff": "1.5"
}' http://0.0.0.0:8536/predict_collisions

  

curl -X POST -H "Content-Type: application/json" -d '{
        "location_id": "200",
        "dowk": "4",
        "hour": "12" 
    }' http://0.0.0.0:8534/predict_collisions

curl -X POST -H "Content-Type: application/json" -d '{
        "location_id": "100",
        "dowk": "4",
        "hour": "16" 
    }' http://0.0.0.0:8534/predict_collisions