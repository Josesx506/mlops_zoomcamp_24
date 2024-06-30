import s3fs
import boto3
import os
import pandas as pd
from datetime import datetime

# Access the LocalStack s3 bucket using either boto3 or s3fs
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:4569")
s3_client = boto3.client("s3", endpoint_url=S3_ENDPOINT_URL)
fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url": S3_ENDPOINT_URL})
print("Avalaible buckets are " + fs.ls("s3://")[0])




def dt(hour, minute, second=0):
    return datetime(2022, 1, 1, hour, minute, second)

def get_output_path(year, month):
    default_output_pattern = "s3://nyc-duration/in/year={year:04d}/month={month:02d}/files.parquet"
    output_pattern = os.getenv("INPUT_FILE_PATTERN", default_output_pattern)
    return output_pattern.format(year=year, month=month)

def prepare_data(df,categorical=["PULocationID", "DOLocationID"]):
    df["duration"] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df["duration"] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype("int").astype("str")
    
    return df

data = [
    (None, None, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2), dt(1, 10)),
    (1, 2, dt(2, 2), dt(2, 3)),
    (None, 1, dt(1, 2, 0), dt(1, 2, 50)),
    (2, 3, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),     
]


columns = ["PULocationID", "DOLocationID", "tpep_pickup_datetime", "tpep_dropoff_datetime"]
df = pd.DataFrame(data, columns=columns)
df = prepare_data(df)

# Save locally to get the file size
local_out = "output/file.parquet"
df.to_parquet(local_out, engine="pyarrow", index=False)
print(f"The file size is {os.stat(local_out).st_size}")
# Save the local file to s3 and print out the files within that folder
# fs.put(output_file,"nyc-duration/2022/01/file.parquet")

# Write file directly to s3
output_file = get_output_path(2022,1)
options = {
    "client_kwargs": {
        "endpoint_url": S3_ENDPOINT_URL
    }
}
df.to_parquet(output_file, engine="pyarrow", compression=None,
              index=False, storage_options=options)


# Print out the files within the target folder
print(fs.ls("s3://nyc-duration/"))