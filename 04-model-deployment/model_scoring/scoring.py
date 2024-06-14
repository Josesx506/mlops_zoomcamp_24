import os
import pickle
from uuid import uuid4

import mlflow
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from sklearn.metrics import root_mean_squared_error

tracking_uri = os.getenv("TRACKING_URI")
RUN_ID = os.getenv("RUN_ID")
S3_BUCKET = os.getenv("S3_BUCKET")

def load_model(mlflow_uri,s3_bucket,run_id):
    mlflow.set_tracking_uri(mlflow_uri)
    model_uri = f"s3://{s3_bucket}/1/{run_id}/artifacts/model"
    loaded_model = mlflow.pyfunc.load_model(model_uri)
    return loaded_model

model = load_model(tracking_uri,S3_BUCKET, RUN_ID)

app = Flask("duration_prediction")

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

def prepare_features(query):
    year = int(query["year"])
    month = int(query["month"])
    taxi = query["taxi"]
    data_url =  f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi}_tripdata_{year:04d}-{month:02d}.parquet"
    df = read_dataframe(data_url)
    df["ride_ids"] = [str(uuid4()) for i in range(len(df))]
    features = prepare_dictionaries(df)

    return features, df["duration"].to_numpy()

def predict(features):
    preds = model.predict(features)
    return preds

@app.route("/predict", methods=["POST"])
def get_ride_duration():
    query = request.get_json()
    features, y_true = prepare_features(query)
    y_pred = predict(features)
    score = root_mean_squared_error(y_pred, y_true)
    mean_dur = np.mean(y_pred)

    result = {
        "score": f"{score:.4f}",
        "mean trip dur": f"{mean_dur:.4f} minutes"
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = 2024)