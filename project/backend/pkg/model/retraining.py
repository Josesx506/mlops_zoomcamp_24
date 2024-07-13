import json
import os
from datetime import datetime, timedelta

import pytz
import requests
from pkg.model.train import training_pipeline
from pkg.model.utils import format_time, get_data_dir


def calculate_training_dates(last_access,tz="US/Eastern",
                             out_fmt="%Y-%m-%dT%H:%M:%S"):

    utc = pytz.utc
    tz = pytz.timezone(tz)
    last_access = last_access.split(" ")[0]
    mid_train = datetime.strptime(last_access, "%Y-%m-%d")
    mid_train = mid_train.astimezone(tz)

    start_train = (mid_train - timedelta(days=30)).strftime(out_fmt)
    end_train = (mid_train + timedelta(days=30)).strftime(out_fmt)
    end_validation = (mid_train + timedelta(days=60)).strftime(out_fmt)

    return start_train, end_train, end_validation

def retrain_pipeline(data_uri="https://data.cityofnewyork.us/resource/h9gi-nx95.json"):
    """
    Retrain the registry models.
        Check the NYC data api for when new accident data is available. 
        If there's no new data, exit the retraining pipeline.
        If the json file checkpoint for the last available dataset is unavailable,
        start training the model from January 2023.
    """
    data_dir = get_data_dir()
    last_data = f"{data_dir}/last_accessed.json"

    if os.path.isfile(last_data):
        with open(last_data, mode="r", encoding="utf-8") as f_in:
            last_access_dt = json.load(f_in)["last_access"]
        
        train_bg_dt,train_ed_dt,val_ed_dt = calculate_training_dates(last_access_dt)

        resps = requests.get(f"{data_uri}?$where=crash_date BETWEEN '{train_ed_dt}' AND '{val_ed_dt}'")
        status_code = resps.status_code

        if status_code == 200:
            train_bg_dt = train_bg_dt.split("T")[0]
            train_ed_dt = train_ed_dt.split("T")[0]
            val_ed_dt = val_ed_dt.split("T")[0]
            train_dt= {"start":train_bg_dt, "end":train_ed_dt}
            test_dt= {"start":train_ed_dt,  "end":val_ed_dt}
            training_pipeline(train_dt, test_dt)
        else:
            print(f"{format_time()}: Insufficient additional data for retraining, exiting now")
    else:
        # Default start date for training data
        train_dt= {"start":"2023-01-01", "end":"2023-03-01"}
        test_dt= {"start":"2023-03-01","end":"2023-03-31"}
        training_pipeline(train_dt, test_dt)


if __name__ == "__main__":
    retrain_pipeline()