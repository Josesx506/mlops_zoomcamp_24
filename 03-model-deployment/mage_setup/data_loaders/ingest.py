import requests
from io import BytesIO
from typing import List

import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader


@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:
    dfs: List[pd.DataFrame] = []

    year = 2023
    month = 3
    
    response = requests.get(
        f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet'
    )

    if response.status_code != 200:
        raise Exception(response.text)

    df = pd.read_parquet(BytesIO(response.content))
    dfs.append(df)

    return pd.concat(dfs)