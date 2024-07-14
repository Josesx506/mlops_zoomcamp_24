### Project Description
Predict number of motor vehicle incidents based on `location_id | dayOfWeek | hourOfDay` in NYC. This can provide crash history alerts to drivers at the start of their journey (by modeling a preferred route between two points in this simple implementation) or dynamic alerts based on proximity to a specific location as the crow flies on their chosen routes. This project was inspired by a [Waze alert](https://blog.google/waze/crash-history-alerts-arrive-to-the-waze-map/) that I got on a recent journey.

<br>
`npx webpack --watch`

### Data and Tools
- [ ] [Maps](https://leafletjs.com/)
- [ ] [Geocoding](https://smeijer.github.io/leaflet-geosearch/)
- [ ] [AOI Masking](https://github.com/ptma/Leaflet.Mask/blob/master/README.md)
- [ ] [Motor Vehicle Collisions](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data)


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


docker build --no-cache --build-arg AWS_ACCESS_KEY_ID=$AWS_KEY --build-arg AWS_SECRET_ACCESS_KEY=$AWS_SECRET_KEY --build-arg AWS_DEFAULT_REGION=$AWS_REGION -t mlserver:v1 -f docker-files/Dockerfile.mlserver .

docker run --rm -p 8534:8534 mlserver:v1 &

<!-- poetry export --without-hashes --format=requirements.txt > requirements.txt -->
docker build -t mlserver:v1 --file Dockerfile.mlserver 


poetry export --without-hashes --format=requirements.txt > requirements.txt




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