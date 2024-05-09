from datetime import datetime,timedelta
import json
import os
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
    
    def stream_data(self):
        resps = requests.get(f"{self.data_uri}?$where=crash_date BETWEEN '{self.strt_dt}' AND '{self.end_dt}'")
        msg = resps.json()
        dump = json.dumps(msg, indent=4, sort_keys=True)
        new_dt = self.utc_dt + timedelta(hours=24)
        self.utc_dt = new_dt
        self.update_time()
        return dump



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
            connection.send(data.encode("utf-8"))
            # Wait for 60 seconds before updating the data
            time.sleep(60)
        except Exception as e:
            print("failed:", e)
        finally:
            # Close the connection
            connection.close()