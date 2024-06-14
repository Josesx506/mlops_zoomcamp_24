import json
import os
import pickle
import sys
import tempfile
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
import logging
import numpy as np
import pandas as pd
from sklearn.metrics import root_mean_squared_error


def load_model():
    with open("model.bin", "rb") as f_in:
        (dv, loaded_model) = pickle.load(f_in)
    return dv, loaded_model

def read_dataframe(filename: str):
    df = pd.read_parquet(filename)
    
    df["duration"] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df["duration"] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    categorical = ["PULocationID", "DOLocationID"]
    df[categorical] = df[categorical].fillna(-1).astype("int").astype("str")
    return df

def prepare_dictionaries(df: pd.DataFrame):
    categorical = ["PULocationID", "DOLocationID"]
    dicts = df[categorical].to_dict(orient="records")
    return dicts

def prepare_features():
    taxi = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    data_url =  f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi}_tripdata_{year:04d}-{month:02d}.parquet"
    df = read_dataframe(data_url)
    features = prepare_dictionaries(df)

    return features, df["duration"].to_numpy()

def predict(model, dv, features):
    X = dv.transform(features)
    preds = model.predict(X)
    return preds

def post_process_file(pred):
    print("saving file to tmp directory ...")
    temp_dir = tempfile.TemporaryDirectory()
    ride_ids = [str(uuid4()) for i in range(len(pred))]
    df = pd.DataFrame({"ride_ids":ride_ids,"ride_dur_min":pred})
    file_name = f"{temp_dir.name}/outfile.parquet"
    df.to_parquet(file_name,index=False)

    # s3 = boto3.client("s3")
    # BUCKET_NAME = os.getenv("S3_BUCKET")

    # try:
    #     with open(file_name, "rb") as f:
    #         s3.upload_file(f, BUCKET_NAME, os.path.basename(file_name))
    # except ClientError as e:
    #     print(e)
    
    
    temp_dir.cleanup()


def get_ride_duration():
    dv, model = load_model()
    features, y_true = prepare_features()
    y_pred = predict(model, dv, features)
    # Save the file to a temporary directory
    post_process_file(y_pred)
    score = root_mean_squared_error(y_pred, y_true)
    mean_dur = np.mean(y_pred)

    result = {
        "score": f"{score:.4f}",
        "mean pred dur": f"{mean_dur:.2f} minutes"
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    get_ride_duration()