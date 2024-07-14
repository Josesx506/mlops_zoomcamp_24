import os
import warnings
from pprint import pprint

import mlflow
import pandas as pd
from hyperopt import STATUS_OK, Trials, fmin, tpe
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from pkg.model.data import download_data
from pkg.model.models import load_all_models, model_hyperparameters
from pkg.model.utils import format_time, get_data_dir, remove_local_artifacts
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_squared_error, root_mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", message=".*Hint: Inferred schema contains integer column(s).*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*mlflow.utils.autologging_utils: You are using an unsupported version of.*", category=UserWarning)

# Check if a remote model registry exists, else use a local registry
MLFLOW_TRACKING_URI = os.getenv("MODEL_REGISTRY_URI")
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "nyc-motor-collisions")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

# Suppress mlflow error logs
mlflow.sklearn.autolog(silent=True)
mlflow.xgboost.autolog(silent=True)


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


def make_pipeline(model,numeric_features=["location_id", "dowk", "hour"]):
    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])

    preprocessor = ColumnTransformer(transformers=[("numerical", numeric_transformer, numeric_features),])
    pipeline = Pipeline(steps=[("preprocessor", preprocessor),
                               ("model", model)])
    return pipeline


def train_base_models(train_dt:dict={"start":"2023-01-01",
                                     "end":"2023-01-02"},
                      test_dt:dict={"start":"2023-03-01",
                                    "end":"2023-03-02"}):
    """
    Train all the models using default hyperparameters to get the best performing model

    Args:
        train_dt (dict, optional): Training data date key-value pairs. Defaults to {"start":"2023-01-01", "end":"2023-01-02"}.
        test_dt (dict, optional): Test data date key-value pairs. Defaults to {"start":"2023-03-01", "end":"2023-03-02"}.

    Returns:
        Tuple (pd.DataFrame, dict): evaluation metrics and training data used
    """
    Xtrain,ytrain = create_data(train_dt["start"], train_dt["end"])
    Xtest,ytest = create_data(test_dt["start"], test_dt["end"], mode="test")

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

            pipeln = make_pipeline(model_cls)

            pipeln.fit(Xtrain,ytrain)
            ypred = pipeln.predict(Xtest)

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

    data = {"train": {"Xtrain": Xtrain, "ytrain": ytrain},
            "test": {"Xtest": Xtest, "ytest": ytest}}
    
    return metric_table, data


def get_best_n_registry_models(n=3):
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

def register_best_model(model_name = os.getenv("PRD_MODEL_NAME",
                                               "nyc-vhc-col-regressor")):
    best_model = get_best_n_registry_models(1)[0]

    all_reg_models = client.search_registered_models()

    if len(all_reg_models) == 0:
        run_id = best_model["run_id"]
        model_uri = f"runs:/{run_id}/models_mlflow"
        model_class = best_model["model_class"]
        mlflow.register_model(model_uri=model_uri,name=model_name)
        print(f"{format_time()}: Registered {model_class} model with uri://{run_id}")
    else:
        all_reg_models = [dict(rg_md) for rg_md in all_reg_models]

        run_id = best_model["run_id"]
        best_model_uri = f"runs:/{run_id}/models_mlflow"
        model_class = best_model["model_class"]

        for model_dict in all_reg_models:
            if model_dict["name"] == model_name:
                for key,value in dict(model_dict["latest_versions"][0]).items():
                    if key=="run_id" and value!=run_id:
                        mlflow.register_model(model_uri=best_model_uri,name=model_name)
                        print(f"{format_time()}: Registered {model_class} model with uri://{run_id}")
                    elif key=="run_id" and value==run_id:
                        print(f"{format_time()}: Best model is already active, exiting pipeline ......")
                    else:
                        pass
    return None


def training_pipeline(train_dt:dict={"start":"2023-01-01",
                                     "end":"2023-01-02"},
                      test_dt:dict={"start":"2023-03-01",
                                    "end":"2023-03-02"},
                      random_state=42):
    """
    Merge the entire pipeline.
    The steps executed by this pipeline are
        - Download training and validation data
        - Train all the model options with default hyperparameters
        - Rank the top 3 performant models from the model registry
        - Perform hyperparameter tuning on the top 3 models
        - Promote the best model to production
    
    Returns:
        None 
    """
    print(f"{format_time()}: Training Base Model  ........")
    df_base_metrics, inp_data = train_base_models(train_dt,test_dt)
    
    # Load the training and test data
    Xtrain,ytrain = inp_data["train"]["Xtrain"],inp_data["train"]["ytrain"]
    Xtest,ytest = inp_data["test"]["Xtest"],inp_data["test"]["ytest"]

    # Extract the top 3 models from the MLflow registry
    top_3_mods = get_best_n_registry_models(n=3)
    top_3_names = [md["model_class"] for md in top_3_mods]
    print(f"{format_time()}: The top 3 models {top_3_names}")
    
    print(f"{format_time()}: Starting hyperparameter tuning  ........")
    # Run hyperparameters tuning on the best models
    model_options = load_all_models()
    model_names = [type(md_cls()).__name__ for md_cls in model_options]
    for model_dict in top_3_mods:
        params_space = model_hyperparameters(model_dict["model_class"], 
                                             random_state=random_state)
        target_model = model_options[model_names.index(model_dict["model_class"])]

        def __objective__(params):
            """
            Objective function to finetune the model hyperparameters
            """
            with mlflow.start_run():
                mlflow.set_tag("model_class", model_dict["model_class"])
                mlflow.log_params(params)

                model = target_model(**params)
                pipeln = make_pipeline(model)

                pipeln.fit(Xtrain,ytrain)

                ypred = pipeln.predict(Xtest)

                rmse = root_mean_squared_error(ytest, ypred)
                mse = mean_squared_error(ytest, ypred)

                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("mse", mse)
                
            return dict(loss=rmse, status=STATUS_OK)

        best_result = fmin(fn=__objective__,
                           space=params_space,
                           algo=tpe.suggest,
                           max_evals=10,
                           trials=Trials())
    
    print(f"{format_time()}: Registering best model  ........")
    register_best_model()

    return None




if __name__ == "__main__":
    train_dt= {"start":"2023-01-01", "end":"2023-03-01"}
    test_dt= {"start":"2023-03-01","end":"2023-03-31"}
    training_pipeline(train_dt, test_dt)
    # remove_local_artifacts()