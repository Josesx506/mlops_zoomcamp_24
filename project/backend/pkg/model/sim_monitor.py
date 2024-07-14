import logging
import os
import random
import time
from datetime import date, datetime, timedelta

import pandas as pd
import psycopg
from evidently import ColumnMapping
from evidently.metrics import (ColumnDriftMetric, DatasetDriftMetric,
                               DatasetMissingValuesMetric)
from evidently.report import Report
from pkg.app.load_model import load_trained_model
from pkg.model.data import download_data
from prefect import flow, task
from sklearn.metrics import root_mean_squared_error

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
dbhost = os.getenv("DB_HOST", "localhost")
dbport = os.getenv("DB_PORT", "5436")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	prediction_drift integer,
	num_drifted_columns integer,
	share_missing_values integer,
    rmse float
)
"""

model = load_trained_model("s3")

num_features = ["location_id", "dowk", "hour"]
column_mapping = ColumnMapping(
    prediction="incidents",
    numerical_features=num_features,
    target=None
)

report = Report(metrics = [
    ColumnDriftMetric(column_name="incidents"),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])

@task
def prep_db():
	with psycopg.connect(f"host={dbhost} port={dbport} user=postgres password=zmcp24", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
		with psycopg.connect(f"host={dbhost} port={dbport} dbname=test user=postgres password=zmcp24") as conn:
			conn.execute(create_table_statement)

@task
def calculate_metrics_postgresql(curr, refr_start, cur_start, i):
    refr_start = refr_start.replace(day=i)
    cur_start = cur_start.replace(day=i)
    refr_end = refr_start + timedelta(days=1)
    cur_end = cur_start + timedelta(days=1)

    refr_data_dt= {"start":str(refr_start), "end":str(refr_end)}
    cur_data_dt= {"start":str(cur_start),"end":str(cur_end)}

    refr_data = download_data(refr_data_dt["start"],refr_data_dt["end"])
    current_data = download_data(cur_data_dt["start"],cur_data_dt["end"])

    current_data["location_id"] = current_data["location_id"].astype("int64")

    y_true = current_data["incidents"]
    current_data = current_data.drop(columns="incidents")

    y_pred = model.predict(current_data[num_features].fillna(0))
    rmse = root_mean_squared_error(y_pred, y_true)
    current_data["incidents"] = y_pred

    report.run(reference_data = refr_data, current_data = current_data, column_mapping=column_mapping)

    result = report.as_dict()

    prediction_drift = result["metrics"][0]["result"]["drift_score"]
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]
    share_missing_values = result["metrics"][2]["result"]["current"]["share_of_missing_values"]

    curr.execute(
        "insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values, rmse) values (%s, %s, %s, %s, %s)",
        (cur_start, prediction_drift, num_drifted_columns, share_missing_values, rmse)
    )
	

@flow
def batch_monitoring_backfill():
    prep_db()
    last_send = datetime.now() - timedelta(seconds=10)
    with psycopg.connect(f"host={dbhost} port={dbport} dbname=test user=postgres password=zmcp24", autocommit=True) as conn:
        for i in range(1, 22):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, refr_start, cur_start, i)
            
            new_send = datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + timedelta(seconds=10)
            logging.info("data sent")
    conn.close()

if __name__ == "__main__":
    refr_start = date(2023, 3, 1)
    cur_start = date(2023, 4, 1)
    batch_monitoring_backfill()
