from pprint import pprint

import mlflow
import pandas as pd
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from pkg.data import download_data
from pkg.models import load_all_models
from pkg.utils import get_data_dir, remove_local_artifacts
from sklearn.metrics import mean_squared_error, root_mean_squared_error

MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "nyc-motor-collisions"

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

mlflow.sklearn.autolog()
mlflow.xgboost.autolog()


def create_data(start:str,end:str,mode="train",target="incidents"):
    """
    Create X and y data for training the model
    """
    df = download_data(start, end, mode=mode, save=True)
    df = df.astype({"location_id":int,"dowk":int,"hour":int,"incidents":float})
    features = df.columns.to_list()
    features.remove(target)
    
    X = df[features]#.to_numpy()
    y = df[target]#.to_numpy()
    
    return X,y


def train_base_models():
    """
    Train all the models using default hyperparameters to get the best
    performing model

    Returns:
        pd.DataFrame: evaluation metrics
    """
    # Xtrain,ytrain = create_data("2023-01-01", "2023-03-01")
    # Xtest,ytest = create_data("2023-03-01", "2023-03-31", mode="test")
    Xtrain,ytrain = create_data("2023-01-01", "2023-01-02")
    Xtest,ytest = create_data("2023-03-01", "2023-03-02", mode="test")

    ensemble_models = load_all_models()

    merged_metrics = {}

    for model_cls in ensemble_models:

        with mlflow.start_run(nested=True) as run:

            model_cls = model_cls()
            model_name = type(model_cls).__name__

            mlflow.set_tag("developer", "Joses")
            mlflow.set_tag("model_class", model_name)
            data_dir = get_data_dir()
            mlflow.log_param("train-data-path", f"{data_dir}/train.parquet")
            mlflow.log_param("valid-data-path", f"{data_dir}/test.parquet")


            model_cls.fit(Xtrain,ytrain)
            ypred = model_cls.predict(Xtest)

            rmse = root_mean_squared_error(ytest, ypred)
            mse = mean_squared_error(ytest, ypred)
            metrics = dict(mse=mse, rmse=rmse)

            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("mse", mse)

            if model_name == "XGBRegressor":
                mlflow.xgboost.log_model(model_cls, model_name)
            else:
                mlflow.sklearn.log_model(model_cls, model_name)

            merged_metrics[model_name] = metrics

    metric_table = pd.DataFrame(merged_metrics).T
    
    return metric_table


def get_best_base_models(n=3):
    """
    Get the run information for the best n models. Defaults to top 3

    Returns:
        list: list with embedded dictionaries
    """
    experiments = client.search_experiments(order_by=["experiment_id DESC"])
    for exp in experiments:
        if dict(exp)["name"] == EXPERIMENT_NAME:
            actv_exp = dict(exp)

    # List all runs associated with an experiment
    runs = client.search_runs(experiment_ids=actv_exp["experiment_id"],
                            filter_string="",
                            run_view_type=ViewType.ACTIVE_ONLY,
                            max_results=n,
                            order_by=["metrics.rmse ASC"])
    
    top_n_models = []

    for run in runs:
        run_info = {"run_id": run.info.run_id,
                    "run_name": run.info.run_name,
                    "mse": run.data.metrics["mse"],
                    "rmse": run.data.metrics["rmse"],
                    "model_class": run.data.tags["model_class"]}
        top_n_models.append(run_info)
    
    return top_n_models


def training_pipeline(random_state=42):
    """
    Merge the entire pipeline
    """
    df_base_metrics = train_base_models()
    top_3_mods = get_best_base_models()
    # Run hyperparameters tuning on the best models
    
    pprint(top_3_mods)
    pass


print(training_pipeline())


# remove_local_artifacts()
