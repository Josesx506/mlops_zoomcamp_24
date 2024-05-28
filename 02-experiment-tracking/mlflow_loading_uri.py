import os
import pickle
import sys
import tempfile

import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
from sklearn.metrics import root_mean_squared_error

sys.path.insert(0, os.getcwd())

from env import MLFLOW_TRACKING_URI

# mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
# client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

# # Manual model loading for a model run
# logged_model = "runs:/a58344d23ea342ee89b403082a014dd4/models_mlflow"
# # Load model as a PyFuncModel or
# mlf_model = mlflow.pyfunc.load_model(logged_model)
# # Load the model as a XGBoost model.
# xgb_model = mlflow.xgboost.load_model(logged_model)
# print(xgb_model)


run_id = "a58344d23ea342ee89b403082a014dd4"
model_name = "nyc-taxi-regressor"
version = "1"

class TestModel:
    def __init__(self, track_uri, run_uri, model_name, model_ver) -> None:
        self.tracking_uri = track_uri
        self.run_uri = run_uri
        self.modelName = model_name
        self.modelVersion = model_ver
        self.register_clients()
        self.load_DV_preprocessor()
        self.load_model()

    def register_clients(self):
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient(self.tracking_uri)

    def load_DV_preprocessor(self):
        # Load Dictionary Vectorizer preprocessor. Download it to the working directory
        temp_dir = tempfile.TemporaryDirectory()
        self.client.download_artifacts(run_id=self.run_uri, path="preprocessor", dst_path=temp_dir.name)
        with open(f"{temp_dir.name}/preprocessor/preprocessor.b", "rb") as f_in:
            self.dv = pickle.load(f_in)
        temp_dir.cleanup()
    
    def load_model(self):
        self.model = mlflow.pyfunc.load_model(f"models:/{self.modelName}/{self.modelVersion}")
    
    def read_dataframe(self, filename):
        df = pd.read_parquet(filename)

        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)

        df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
        df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

        df = df[(df.duration >= 1) & (df.duration <= 60)]

        categorical = ["PULocationID", "DOLocationID"]
        df[categorical] = df[categorical].astype(str)
        
        return df

    def preprocess(self, df):
        df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]
        categorical = ["PU_DO"]
        numerical = ["trip_distance"]
        train_dicts = df[categorical + numerical].to_dict(orient="records")
        return self.dv.transform(train_dicts)
    
    def test_model(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        return {"rmse": root_mean_squared_error(y_test, y_pred)}

    def execute_workflow(self,datapath):
        df = self.read_dataframe(datapath)
        X_test = self.preprocess(df)
        y_test = df["duration"].to_numpy()
        pred = self.test_model(X_test, y_test)
        return pred
    

mlfTest = TestModel(MLFLOW_TRACKING_URI,run_id,model_name,version)
result = mlfTest.execute_workflow("data/hw2/train/green_tripdata_2023-03.parquet")
print(result)