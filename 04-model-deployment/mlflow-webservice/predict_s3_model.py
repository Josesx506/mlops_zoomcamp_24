import pickle
import tempfile

import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient
from sklearn.metrics import root_mean_squared_error

# Remote ec2 server link
tracking_uri = "http://ec2-100-26-136-60.compute-1.amazonaws.com:5000"

mlflow.set_tracking_uri(tracking_uri)

RUN_ID = "463c2a7966b84dd5b84b0ad3ca7c64ba"
S3_BUCKET = "mlflow-artifacts-joses"
model_uri = f"s3://{S3_BUCKET}/1/{RUN_ID}/artifacts/model"

# Load model as a PyFuncModel. 
# This is an sklearn pipeline that has the preprocessor and trained model
loaded_model = mlflow.pyfunc.load_model(model_uri)


# Predict on a Pandas DataFrame.
def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df["duration"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].astype(str)
    return df


def prepare_dictionaries(df: pd.DataFrame):
    df["PU_DO"] = df["PULocationID"] + "_" + df["DOLocationID"]
    categorical = ["PU_DO"]
    numerical = ["trip_distance"]
    dicts = df[categorical + numerical].to_dict(orient="records")
    return dicts

df_pred = read_dataframe(f"https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2021-03.parquet")
target = "duration"
y_val = df_pred[target].values

dict_pred = prepare_dictionaries(df_pred)

y_pred = loaded_model.predict(dict_pred)
print(y_pred)