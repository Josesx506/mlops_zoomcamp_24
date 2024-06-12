from typing import Tuple

from pandas import Series
from scipy.sparse._csr import csr_matrix
from sklearn.base import BaseEstimator
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error

import mlflow
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
import os
import pickle
import tempfile
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe


if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


# I set MLFlow port to 3500 in the docker image
DEFAULT_TRACKING_URI = 'http://mlflow:3500'
DEFAULT_DEVELOPER = os.getenv('EXPERIMENTS_DEVELOPER', 'joses')
DEFAULT_EXPERIMENT_NAME = 'nyc-taxi-experiment'


client = MlflowClient(tracking_uri=DEFAULT_TRACKING_URI)
mlflow.set_tracking_uri(DEFAULT_TRACKING_URI)
mlflow.set_experiment(DEFAULT_EXPERIMENT_NAME)


mlflow.sklearn.autolog(disable=True)


def save_DV_preprocessor(binFile,fpath="preprocessor.b"):
    # Load Dictionary Vectorizer preprocessor. Download it to the working directory
    temp_dir = tempfile.TemporaryDirectory()
    fname = f"{temp_dir.name}/{fpath}"
    with open(fname, "wb") as f_out:
        pickle.dump((binFile), f_out)
    mlflow.log_artifact(fname, artifact_path="preprocessor")
    temp_dir.cleanup()


@custom
def transform_custom(build_output: Tuple[csr_matrix,Series,BaseEstimator],
    *args, **kwargs):
    """
    args: The output from any upstream parent blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    # Specify your custom logic here
    X_train, y_train, dv = build_output

    try:
        with mlflow.start_run():
            save_DV_preprocessor(dv)

            lr = LinearRegression()
            lr.fit(X_train,y_train)

            y_pred = lr.predict(X_train)
            mse = root_mean_squared_error(y_train, y_pred)
            mlflow.log_metric("mse", mse)
            save_DV_preprocessor(lr, "lin_reg.bin")
    
    except Exception as e:
        print(f"MLflow run failed: {e}")
    
    finally:
        # Ensure that the run is ended
        mlflow.end_run()

    print(f"tracking URI: '{mlflow.get_tracking_uri()}'")
    return {}
