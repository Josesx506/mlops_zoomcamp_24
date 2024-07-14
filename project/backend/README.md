### Backend Docs
The backend is split into 2 parts, the `model` and `app` parts. The `model` section involves all the steps used to train, and retrain the ML models. [Data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data) is acquired from the NYC Motor Collision [api](https://data.cityofnewyork.us/resource/h9gi-nx95.json). The API has a max limit of *1000* rows, so queries between 2 dates are extracted by filtering the api calls into daily segments.

### Setup
Dependencies are managed by ***poetry*** with a minimum python version of 3.11. 
- Run the `make setup` command to install all the local requirements.
- My model registry is setup on an AWS EC2 instance but you can launch a local server with `mlflow server` to test the script. Navigate to `http://http://127.0.0.1:5000/` to view the mlflow ui.
- Once your server is up and running, you can train the model using the instructions in the next section.

### Model
A list of models are trained/retrained by default in the `pkg/model/models.py` file. The main training pipeline function is *`training_pipeline()`*. It can be accessed using the example below

```python
from pkg.model.train import training_pipeline

if __name__ == "__main__":
    train_dt= {"start":"2023-01-01", "end":"2023-03-01"}
    test_dt= {"start":"2023-03-01","end":"2023-03-31"}
    training_pipeline(train_dt, test_dt)
```

A list of initial models are trained with the default hyperparameters. Hyperparameter tuning is then performed on the top 3 models in the registry, and the models are evaluated on the validation dataset. The best model is registered as the primary model in the registry or retained. <br>

The earliest dates for training the model is set to January 1, 2023, although collision data exists for earlier dates. Each time data is downloaded, the script saves a json file indicating the last date when the api was accessed. For retraining, the script checks if new data is available on the api past the last accessed date, and then it triggers the training pipeline.

```python
from pkg.model.retraining import retrain_pipeline

if __name__ == "__main__":
    retrain_pipeline()
```

No arguments are passed to the retraining pipeline. The retraining pipeline repeats the same training technique on the updated datasets. If no performance improvement is achieved with the new dataset the previous best model is retained, else the new model is promoted for predictions.

#### Orchestration (No Prefect/Mage/Kubeflow)
Orchestration is fully deployed via `Github actions` to minimize the complexity of setting up a MAGE environment on AWS. MAGE was easy to understand but complex to setup without copying the zoomcamp docker image and I didn't really learn the Prefect module last year. The retraining pipeline is setup as a cron job that is triggered ***bi-weekly / monthly***. This reduces the orchestration quality because dashboards are not available to vizualize the models performance. *(I can implement a custom dashboard to push performance logs to the grafana postgres db).*


### App
Flask