import os

import mlflow
from mlflow.tracking import MlflowClient


def load_trained_model(mode="mlflow-registry"):
    # Check if a remote model registry exists, else use a local registry
    MLFLOW_TRACKING_URI = os.getenv("MODEL_REGISTRY_URI")
    EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "nyc-motor-collisions")

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

    model_name = os.getenv("PRD_MODEL_NAME", "nyc-vhc-col-regressor")
    model_meta_data = dict(client.get_registered_model(model_name))

    if mode == "mlflow-registry":
        run_id = dict(model_meta_data["latest_versions"][0])["run_id"]
        model_uri = f"runs:/{run_id}/model"
        model = mlflow.pyfunc.load_model(model_uri)
    elif mode == "s3":
        s3_path = dict(model_meta_data["latest_versions"][0])["source"]
        s3_path = s3_path.replace("models_mlflow","model")
        model = mlflow.pyfunc.load_model(s3_path)

    return model
