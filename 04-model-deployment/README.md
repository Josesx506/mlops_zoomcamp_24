### Model deployment
A virtual environment was created with `pipenv`. 
- First create a new virtual environment `python -m venv deploy`
- Activate the virtual environment `source deploy/bin/activate`
- Upgrade pip `pip install --upgrade pip`
- Install pipenv `pip install pipenv`
- Install the packages with pipenv `pipenv install scikit-learn==1.0.2 flask --python=3.12`. Unlike python-dotenv, pipenv allows you to specify the python version.

Updated Pipfile.lock (a092f96c3ff9485f3a8e105218e9b623c8cee98c76a02662b0212b3d4c5ac691)!
Updated Pipfile.lock (cde4ebbb92f751b179709139ec54dbff122291b60738db5d879459e3b8acea3d)!

### Environment Setup
Normally, pipenv creates its own virtual environment and steps 1-3 above can be ignored but I didn't want too many venv managers install to my global python environment so I used a virtual environment. To activate the pipenv virtual environment, execute `pipenv shell` (like *poetry*). Alternatively, run a command inside the virtualenv with `pipenv run`.<br><br>

Pipenv creates a ***Pipfile*** and ***Pipfile.lock*** for managing dependency installations. You can install development dependencies with `pipenv install --dev requests` <br><br>

To reduce the length of the prefix in terminal, run `PS1="> "`. This removes all the preceding file path texts in an environment. <br><br>

I used the lin_reg.bin file from the zoomcamp repo and used a lower scikit-learn version than HW1. 

### Flask
After creating the simple flask app in `flask_predict.py`, use the bash script to start and run it in background locally. 
- Give the script permisssions `chmod +x background_flask.sh`
- Launch the server with `./background_flask.sh start`
- Stop the server with `./background_flask.sh stop`
This ensures you can still use your terminal while testing the script.

To test the script, you can change the query in the `local_flask/test.py` file and put in desired trip parameters. the script also allows you to pass in a custom url but retains default values for ease. After starting the server, you can test the endpoint with
```python
python local_flask/test.py # or
python local_flask/test.py -url="http://0.0.0.0:2024/predict"
```

The endpoint can also be tested with curl e.g.
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "PULocationID": "10",
  "DOLocationID": "50",
  "trip_distance": "20"
}' http://0.0.0.0:2024/predict
```

To use a production server, use `gunicorn` web server instead of flask.
- `cd` into the ***local_flask*** directory and launch the server in another terminal window
- Launch the gunicorn server and target the app variable in the *flask_predict.py* file `gunicorn --bind=0.0.0.0:2024 flask_predict:app`

You can test the endpoint with the python script or curl.

### Docker
A base image has already been provided with the required python version and trained model inside the file. Copy the environment files and prediction scripts into the docker environment and use a custom tag to create the image. There's no need to set a workdir because the baseimage already set it to `app` <br>
The dockerfile I used is 
```docker
FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

COPY [ "Pipfile", "Pipfile.lock", "./"]

COPY [ "docker_flask/predict.py", "./"]

RUN pip install -U pip

RUN pip install pipenv

RUN pipenv install --system --deploy

EXPOSE 2024

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:2024", "predict:app" ]
```

- Build the docker image with `docker build -t zmcp24-ride-dur:v1 .`
- Launch the container in 
    - interative mode `-it`,
    - remove the container once it's shutdown `--rm`, and 
    - expose port 2024 on your system to the docker environment `-p 2024:2024`
    - with `docker run -it --rm -p 2024:2024 zmcp24-ride-dur:v1`
- In interactive mode, you can stop the container with `Ctrl + C`.
- You can also view the image and get the *IMAGE_ID* with `docker images`
- You can delete an image with `docker image rm <IMAGE_ID>`

Because the container is run in interactive mode, muting the output throws errors. Run the container without interactive mode `-it` and minimize the stderr with `docker run --rm -p 2024:2024 zmcp24-ride-dur:v1 &`, 
- Check the running containers with `docker ps -a`
- Get the container id and stop it with `docker container stop <CONTAINER_ID>`
- Test the endpoint with curl as described above. If it runs, your script is good. 

***Note***: The sklearn version in the environment is `v1.5.0` vs `v1.0.2` used in the video exercises.

### MLFlow EC2
1. Create an EC2 instance, I used a t2 micro and download a key to your computer
2. Set the key permissions `chmod 400 <key_name.pem>` using your key name
3. Setup a config file in the ssh folder with the key path and User name. I used Amazons AMI VM so the user is be set to `ec2-user`. If you use an Ubuntu VM, the user should be set to `ubuntu`
    ```bash
        Host  mlflow-ec2
        HostName 35.171.4.205
        User ec2-user
        IdentityFile /Path/to/key.pem
        StrictHostKeyChecking no
    ```
4. Connect to the instance from terminal `ssh <HostName>` from the config above or using vscode ssh extension. I used vscode.
5. It comes with python3 installed so I just installed pip with `sudo yum install python3-pip`, then `pip install pipenv`
6. Install the server dependencies with`pipenv install scikit-learn mlflow numpy pandas pyarrow boto3` and activate the virtual environment with `pipenv shell`.
7. Create an S3 bucket. I created one named `mlflow-artifacts-joses`.
8. Launch an MLFlow server using the bucket to store artifacts `mlflow server --host 0.0.0.0 -p 5000 --backend-store-uri=sqlite:///mlflow.db --default-artifact-root=s3://mlflow-artifacts-joses/`.
    - Set up inbound security rules to allow you access on the desired port, in this case `:5000`.
    - You can also approve traffic from specific ip addresses like your personal ip - Use https://checkip.amazonaws.com/ to confirm your ip address.
    - Sometimes Chrome might just prevent you from connecting to the instances even after inbound rules have been approved. You can clear cache.
    - Click on the public dns link and append the port as a suffix to access the mlflow server. It should resemble `http://ec2-100-26-136-60.compute-1.amazonaws.com:5000` 
9. Train the model using the `train_rf.ipynb` notebook so that the model is saved on the remote server and you can access it from your local script.
10. On your local computer, navigate to the `mlflow-webservice` directory and use the different scripts
    - Use `predict_mlflow_server.py` to use the remote EC2 model local on a different month.
    - Use `predict_s3_model.py` to use the remote mlflow model that has been saved to an s3 bucket in case the mlflow server shuts down.
    - Use `predict_flask.py` to run the remote mlflow model that has been saved to an s3 bucket on a local flask server. You can test the server with the curl query above.



### Homework
Use the `starter.ipynb` notebook
1. Check the prediction standard deviation with `np.std()` - 6.24
2. Check the file size with `ls` - 68641674

