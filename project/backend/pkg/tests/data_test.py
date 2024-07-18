import os

import boto3
import pandas as pd
from pkg.model.data import download_data, load_data, load_shapefile
from pkg.model.utils import get_data_dir

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:4569")
s3_client = boto3.client("s3", endpoint_url=S3_ENDPOINT_URL)

options = {
    "client_kwargs": {
        "endpoint_url": S3_ENDPOINT_URL
    }
}

def test_load_shapefile():
    shp = load_shapefile(s3_client)
    assert shp is not None
    assert shp.crs == "4326"
    assert "borough" in shp.columns

def test_load_data():
    start_date = "2023-01-01"
    end_date = "2023-01-02"
    df = load_data(start_date, end_date)

    first_rec = df.loc[0,"timestamp"].split(" ")[0]
    last_rec = df["timestamp"].to_list()[-1].split(" ")[0]

    assert start_date == first_rec
    assert end_date == last_rec
    assert df is not None
    assert "last_accessed.json" in os.listdir(get_data_dir())

def test_download_data():
    start_date = "2023-01-01"
    end_date = "2023-01-02"
    df = download_data(start_date,end_date)

    assert len(df.columns) == 4
    assert df is not None
    
