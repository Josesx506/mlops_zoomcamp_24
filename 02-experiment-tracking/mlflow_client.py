import os
import sys

import mlflow
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
sys.path.insert(0, os.getcwd())
from pprint import pprint

from env import MLFLOW_TRACKING_URI

client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# List all saved models
for rm in client.search_registered_models():
    pprint(dict(rm), indent=4)

# List all experiments
experiments = client.search_experiments(order_by=["experiment_id DESC"])
for exp in experiments:
    pprint(dict(exp), indent=4)

# List all runs associated with an experiment
runs = client.search_runs(experiment_ids="1",
                          filter_string="",
                          run_view_type=ViewType.ACTIVE_ONLY,
                          max_results=5,
                          order_by=["metrics.rmse ASC"])
for run in runs:
    pprint({"run_id": run.info.run_id,
            "run_name": run.info.run_name,
            "rmse": run.data.metrics["rmse"]}, indent=4)

# Register new models or update model versions
run_id = "9d652875f19a4d208075c5d1daa3c8f6"
model_uri = f"runs:/{run_id}/models_mlflow"
model_name = "nyc-taxi-regressor"
# mlflow.register_model(model_uri=model_uri,name=model_name)

