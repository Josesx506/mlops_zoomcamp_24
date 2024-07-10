import os
import sys
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import boto3
import geopandas as gpd
import pandas as pd
import pytz
import requests
from geopandas import GeoDataFrame, points_from_xy
from pkg.utils import get_data_dir
from tqdm import tqdm


def load_shapefile():
    """
    Download the NYC Taxi Zone geojson file from the s3 bucket

    Returns:
        gpd.GeoDataFrame: Boundary data for each zone.
    """
    S3_BUCKET = "mlflow-artifacts-joses"
    s3 = boto3.client("s3")
    temp_file = NamedTemporaryFile(suffix=".geojson")
    s3.download_file(S3_BUCKET,"data/NYCTaxiZones.geojson",temp_file.name)
    gdf = gpd.read_file(temp_file.name)
    temp_file.close()
    return gdf

def generate_incident_labels(df,shp):
    """
    Calculate the total number of incidents in each borough 
    at an hourly resolution.

    An incident is an accident/injury/fatality.

    Args:
        df (pd.DataFrame): Rows of accident data
        shp (gpd.GeoDataFrame): location polygons
    """
    points = GeoDataFrame(df, geometry=points_from_xy(df.longitude, df.latitude), crs="4326")
    bourough_ids = gpd.sjoin(points, shp, how="left", predicate="within")
    bourough_ids["timestamp"] = pd.to_datetime(bourough_ids["timestamp"])
    bourough_ids = bourough_ids[["timestamp","location_id","fatalities","injuries"]]

    # A value of zero represents at least 1 incident
    bourough_ids["incidents"] = bourough_ids["fatalities"] + bourough_ids["injuries"]
    bourough_ids["incidents"] = bourough_ids["incidents"].replace(0,1)

    bourough_ids["dowk"] = bourough_ids["timestamp"].dt.dayofweek
    bourough_ids["hour"] = bourough_ids["timestamp"].dt.hour
    bourough_ids = bourough_ids.drop(columns=["fatalities","injuries","timestamp"])

    tot_incidents = bourough_ids.groupby(["location_id", "dowk", "hour"]).sum().reset_index()
    tot_incidents = tot_incidents.sample(frac=1).reset_index(drop=True)
    return tot_incidents
    

def visualize_single_borough_stats(df:pd.DataFrame, borough_id:str):
    """
    Visualize how the incident stats look like for a location

    Args:
        df (pd.DataFrame): data with number of incident labels
        borough_id (str): borough id from nyc shapefile
    """
    tmp = df[df["location_id"]==borough_id]
    tmp = tmp[["dowk","hour","incidents"]].reset_index(drop=True)
    fata_pvt = tmp.pivot_table(index="dowk", columns="hour", aggfunc="sum", fill_value=0)
    
    import matplotlib.pyplot as plt
    import seaborn as sns

    plt.figure(figsize=(12, 6))
    sns.heatmap(fata_pvt, annot=True, fmt="d", cmap="YlGnBu", cbar=True)
    plt.title('Density of Points for Each Day of the Week and Hour of the Day')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Day of the Week')
    plt.yticks(ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5], labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], rotation=0)
    plt.show()



def load_data(starttime,endtime):
    starttime = datetime.strptime(starttime, "%Y-%m-%d")
    endtime = datetime.strptime(endtime, "%Y-%m-%d")

    days_btw = (endtime - starttime).days
    incr = 1
    daily_dfs = []

    for day in tqdm(range(days_btw), 
                    position=0, desc="Loading NYC Motor Collision data ...."):
        try:
            stop_dt = starttime + timedelta(days=incr)
            day_df = NYCAccidentDataPipe(starttime, stop_dt).pull_data()
            daily_dfs.append(day_df)
        except:
            pass

        starttime = stop_dt
    
    final_df = pd.concat(daily_dfs).reset_index(drop=True)
    
    return final_df

class NYCAccidentDataPipe:
    def __init__(self,strt_dt,end_dt,tz="US/Eastern",
                 uri="https://data.cityofnewyork.us/resource/h9gi-nx95.json",
                 fmt="%Y-%m-%dT%H:%M:%S"
                 ):
        self.tz = pytz.timezone(tz)
        strt_dt = strt_dt.astimezone(self.tz)
        end_dt = end_dt.astimezone(self.tz)
        self.strt_dt = strt_dt.strftime(fmt)
        self.end_dt = end_dt.strftime(fmt)
        self.data_uri = uri
    
    def combination(self,x,y):
        """
        Combine pandas columns

        Args:
            x (pd.Series): column
            y (pd.Series): column

        Returns:
            pd.Series: merged column
        """
        if pd.isna(x):
            x = ""
        if pd.isna(y):
            y = ""
        if x == "" and y == "":
            return "Unspecified"
        if x != "" and y == "":
            return x
        if x == "" and y != "":
            return y
        if x == y or (y in x.split(",")):
            return x
        if x != "" and y != "" and x != y and ("Unspecified" not in [x,y]) and ("UNKNOWN" not in [x,y]):
            return x + "/" + y
    
    def preprocess_json(self,raw_json):
        df = pd.DataFrame(raw_json)
        df = df.dropna(subset=["longitude","latitude"]).reset_index(drop=True)
        df["timestamp"] = df.apply(lambda x: str(pd.to_datetime(x.crash_date.split("T")[0] + "T" + x.crash_time)), axis=1)
        df["contributing_factor"] = df["contributing_factor_vehicle_1"].combine(df["contributing_factor_vehicle_2"], self.combination).combine(df["contributing_factor_vehicle_3"], self.combination).combine(df["contributing_factor_vehicle_4"], self.combination).combine(df["contributing_factor_vehicle_5"], self.combination)
        df["vehicle_type"] = df["vehicle_type_code1"].combine(df["vehicle_type_code2"], self.combination).combine(df["vehicle_type_code_3"], self.combination).combine(df["vehicle_type_code_4"], self.combination).combine(df["vehicle_type_code_5"], self.combination)
        df = df[["timestamp","longitude","latitude",
                 "collision_id","number_of_persons_injured",
                 "number_of_persons_killed","on_street_name",
                 "off_street_name","cross_street_name",
                 "contributing_factor","vehicle_type"]]
        df = df.astype({"collision_id":int,
                        "number_of_persons_injured":int,
                        "number_of_persons_killed":int,
                        "longitude":float,"latitude":float})
        df = df.rename(columns={"number_of_persons_injured":"injuries","number_of_persons_killed":"fatalities"})
        return df
    
    def pull_data(self):
        resps = requests.get(f"{self.data_uri}?$where=crash_date BETWEEN '{self.strt_dt}' AND '{self.end_dt}'")
        msg = resps.json()
        fmt_df = self.preprocess_json(msg)
        return fmt_df

def download_data(starttime=None,endtime=None,mode="train",save=False):
    """
    Download data for either training, validation, or testing.
    It can be run from terminal as 
        - `python pkg/data.py 2016-01-01 2016-03-01 train True`
        - `python pkg/data.py 2016-01-01 2016-03-01 test False`
    or inside a script as
        - `download_data("2016-01-01", "2016-03-01", mode="train", save=True)`
        - `download_data("2016-01-01", "2016-03-01", mode="test", save=False)`

    Args:
        starttime (str, optional): Start date to download data.
        endtime (str, optional): End date to download data.
        mode (str, optional): Check if the data is in train or val mode. Defaults to "train".
        save (bool, optional): Save the file to the data folder. Defaults to False.

    Raises:
        ValueError: If not enough arguments are specified
    
    Returns:
        pd.DataFrame: Preprocessed data
    """
    if (starttime is None) and (endtime is None) and (len(sys.argv) == 5):
        starttime = sys.argv[1]
        endtime = sys.argv[2]
        mode = sys.argv[3]
        save = bool(sys.argv[4])
    elif (starttime is not None) and (endtime is not None):
        pass
    else:
        raise ValueError("`starttime` and `endtime` need to be specified")
    
    save_dir = get_data_dir()

    shp = load_shapefile()
    df = load_data(starttime, endtime)
    labeled_data = generate_incident_labels(df,shp)

    if os.path.exists(save_dir) and save:
        labeled_data.to_parquet(f"{save_dir}/{mode}.parquet")
    
    return labeled_data


if __name__ == "__main__":
    download_data()