import json
import logging
import os
import sys
import tempfile
from datetime import date, datetime, timedelta
from uuid import uuid4
import time

import pandas as pd
import psycopg
from evidently import ColumnMapping
from evidently.metrics import (ColumnCorrelationsMetric, ColumnDriftMetric,
                               ColumnQuantileMetric, DatasetDriftMetric,
                               DatasetMissingValuesMetric)
from evidently.report import Report
from joblib import load
from prefect import flow, task
from sklearn.metrics import root_mean_squared_error

os.system("clear")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


class EvidentlyHW5:
    def __init__(self,taxi,year,month):
        self.taxi = taxi
        self.year = year
        self.month = month


def load_model():
    with open("../models/lin_reg.bin", "rb") as f_in:
        model = load(f_in)
    return model

def read_dataframe(filename: str):
    df = pd.read_parquet(filename)
    print(f"\nThe downloaded dataset shape is {df.shape[0]} rows by {df.shape[1]} columns.\n")
    
    df["duration_min"] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df["duration_min"] = df.duration_min.dt.total_seconds() / 60

    df = df[(df.duration_min >= 1) & (df.duration_min <= 60)].copy()

    cat_features = ["PULocationID", "DOLocationID"]
    df[cat_features] = df[cat_features].fillna(-1).astype("int").astype("str")
    df = df.sort_values(by="lpep_pickup_datetime").reset_index(drop=True)
    return df

def prepare_dictionaries(df: pd.DataFrame):
    num_features = ["passenger_count", "trip_distance", "fare_amount", "total_amount"]
    cat_features = ["PULocationID", "DOLocationID"]
    df[num_features] = df[num_features].interpolate() # Similar to fillna
    dicts = df[num_features+cat_features+["lpep_pickup_datetime"]]
    return dicts

def prepare_features():
    taxi = sys.argv[1]
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    monthname = date(1900, month, 1).strftime("%B")
    data_url =  f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi}_tripdata_{year:04d}-{month:02d}.parquet"
    print(f"Reading data for {taxi.capitalize()} taxi {monthname.capitalize()} {year:04d}!!!!")
    df = read_dataframe(data_url)
    target = "duration_min"
    features = prepare_dictionaries(df)

    return features, df[target].to_numpy()

def predict(model, features):
    X = features.loc[:,~features.columns.isin(["lpep_pickup_datetime"])]
    preds = model.predict(X)
    return preds

def create_evidently_report(reference_data, current_data):
    num_features = ["passenger_count", "trip_distance", "fare_amount", "total_amount"]
    cat_features = ["PULocationID", "DOLocationID"]
    
    column_mapping = ColumnMapping(
        prediction="prediction",
        numerical_features=num_features,
        categorical_features=cat_features,
        target=None
    )

    report = Report(metrics = [
        ColumnDriftMetric(column_name="prediction"),
        DatasetDriftMetric(),
        DatasetMissingValuesMetric(),
        ColumnQuantileMetric(column_name="fare_amount",quantile=0.5),
        ColumnCorrelationsMetric(column_name="prediction")
    ])
    
    report.run(reference_data = reference_data, current_data = current_data,
		column_mapping=column_mapping)
    
    result = report.as_dict()

    return result

def extract_metrics(result):
    prediction_drift = result["metrics"][0]["result"]["drift_score"]
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]
    share_missing_values = result["metrics"][2]["result"]["current"]["share_of_missing_values"]
    fare_amount_quantile_50 = result["metrics"][3]["result"]["current"]["value"]
    pearson_corr_fare_amount = result["metrics"][4]["result"]["current"]["pearson"]["values"]["y"][2]
    
    return {"pred_drift": prediction_drift,
            "n_drift_cols": num_drifted_columns,
            "pct_mssng_vals": share_missing_values,
            "fare_amt_q50": fare_amount_quantile_50,
            "pear_corr_fare_amt": pearson_corr_fare_amount}

@task
def prep_db():
    create_table_statement = """
    drop table if exists dummy_metrics;
    create table dummy_metrics(
        timestamp timestamp,
        prediction_drift float,
        num_drifted_columns integer,
        share_missing_values float,
        fare_amt_q50 float,
        pearson_corr_fare_amt float,
        rmse float
    )
    """
    
    with psycopg.connect("host=localhost port=5436 user=postgres password=example", autocommit=True) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
        with psycopg.connect("host=localhost port=5436 dbname=test user=postgres password=example") as conn:
            conn.execute(create_table_statement)

@task
def calculate_metrics_postgresql(curr, ref_data, all_data, y_true, day):
    year = int(sys.argv[2])
    month = int(sys.argv[3])
    begin = datetime(year, month, 1, 0, 0)
    starttime = begin + timedelta(day)
    endtime = begin + timedelta(day + 1)

    print(f"End date: {endtime}")
    
    current_data = all_data[(all_data.lpep_pickup_datetime >= starttime) &
		(all_data.lpep_pickup_datetime < endtime)]
    
    # Calculate rms error
    start_idx = current_data.index[0]
    end_idx = current_data.index[-1]
    y_true_filt = y_true[start_idx:end_idx+1]
    y_pred = current_data["prediction"]
    rmse = root_mean_squared_error(y_pred, y_true_filt)
    
    result = create_evidently_report(ref_data, current_data)
    dashboard_metrics = extract_metrics(result)

    prediction_drift = dashboard_metrics["pred_drift"]
    num_drifted_columns = dashboard_metrics["n_drift_cols"]
    share_missing_values = dashboard_metrics["pct_mssng_vals"]
    fare_amount_quantile_50 = dashboard_metrics["fare_amt_q50"]
    pearson_corr_fare_amount = dashboard_metrics["pear_corr_fare_amt"]
    
    curr.execute(
		"insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values, fare_amt_q50, pearson_corr_fare_amt, rmse) values (%s, %s, %s, %s, %s, %s, %s)",
		(starttime, prediction_drift, num_drifted_columns, share_missing_values, fare_amount_quantile_50, pearson_corr_fare_amount, rmse)
	)

@flow
def push_evidently_metrics():
    prep_db()
    model = load_model()
    features, y_true = prepare_features()
    
    y_pred = predict(model, features)
    features["prediction"] = y_pred
    reference_data = pd.read_parquet("../data/reference.parquet")
    
    SEND_TIMEOUT = 1

    last_send = datetime.now() - timedelta(seconds=10)
    with psycopg.connect("host=localhost port=5436 dbname=test user=postgres password=example", autocommit=True) as conn:
        for day in range(0, 30):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, reference_data, features, y_true, day)

            new_send = datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + timedelta(seconds=10)
            logging.info("data sent")

if __name__ == "__main__":
    push_evidently_metrics()