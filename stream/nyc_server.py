from datetime import datetime,timedelta
import json
import os
import pandas as pd
import pytz
import requests
import socket
import time


class NYCAccidentStream:
    def __init__(self,uri="https://data.cityofnewyork.us/resource/h9gi-nx95.json",
                 tz="US/Eastern",fmt="%Y-%m-%dT%H:%M:%S") -> None:
        utc = pytz.utc
        self.fmt = fmt
        self.tz = pytz.timezone(tz)
        self.utc_dt = datetime(2016, 1, 1, 5, 0, 0, tzinfo=utc)
        self.data_uri = uri
        self.update_time()
    
    def update_time(self):
        strt_dt = self.utc_dt.astimezone(self.tz)
        self.end_dt = (strt_dt + timedelta(hours=24)).strftime(self.fmt)
        self.strt_dt = strt_dt.strftime(self.fmt)
    
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
        df = df[["timestamp","longitude","latitude","collision_id","number_of_persons_injured","number_of_persons_killed","on_street_name","off_street_name","cross_street_name","contributing_factor","vehicle_type"]]
        df = df.astype({"collision_id":int,"number_of_persons_injured":int,"number_of_persons_killed":int,"longitude":float,"latitude":float})
        df = df.rename(columns={"number_of_persons_injured":"injuries","number_of_persons_killed":"fatalities"})
        preproc = json.loads(df.to_json(orient="records"))
        return preproc
    
    def stream_data(self):
        resps = requests.get(f"{self.data_uri}?$where=crash_date BETWEEN '{self.strt_dt}' AND '{self.end_dt}'")
        msg = resps.json()
        fmt_json = self.preprocess_json(msg)
        # dump = json.dumps(fmt_json, indent=4, sort_keys=True)
        new_dt = self.utc_dt + timedelta(hours=24)
        self.utc_dt = new_dt
        self.update_time()
        return fmt_json



if __name__ == "__main__":
    os.system("clear")
    nyc = NYCAccidentStream()

    # Create a socket
    sock = socket.socket()
    print("Socket created ...")

    localhost = "127.0.0.1"
    port = 1500
    sock.bind((localhost, port))
    sock.listen(5)

    while True:
        # Wait for a connection
        connection, address = sock.accept()
        try:
            data = nyc.stream_data()
            print(f"Returned {len(data)} entries!!!!")
            # print(json.dumps(data[0], indent=4, sort_keys=True))
            connection.send(json.dumps(data, sort_keys=True).encode("utf-8"))
            # Wait for 60 seconds before updating the data
            time.sleep(2)
        except Exception as e:
            print("failed:", e)
        finally:
            # Close the connection
            connection.close()